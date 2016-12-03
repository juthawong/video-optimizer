#!/usr/bin/env python
# encoding: utf-8
import SocketServer
import json
import tqdm
import logging
import os
from pprint import pformat
from sh import ffprobe as _ffprobe, ffmpeg as _ffmpeg
from threading import Thread
from video_optimizer import cast_type, Dict

log = logging.getLogger(__name__)


def ffprobe(*args, **kwargs):
    return Dict(
        cast_type(
            json.loads(
                _ffprobe(
                    '-print_format',
                    'json',
                    *args,
                    **kwargs
                ).stdout
            )
        )
    )


def ffmpeg(*args, **kwargs):
    try:
        result = _ffmpeg(
            _iter=True,
            _err_to_out=True,
            *args, **kwargs
        )

        for line in result:
            print(line.strip())

    except Exception as e:
        print(e.stdout)
        print(e.stderr)
        raise


def create_handler(total):
    class ProgressHandler(SocketServer.StreamRequestHandler):
        bar_format = "{desc}{percentage:3.0f}% {bar} [{elapsed} ETA: {remaining}]"

        def handle(self):
            with tqdm.tqdm(total=total, unit='ms', bar_format=self.bar_format) as progressbar:
                old = 0

                while True:
                    line = self.rfile.readline().strip()
                    if not line:
                        continue

                    key, value = line.split("=")

                    if key != "out_time_ms":
                        continue

                    value = cast_type(value)
                    delta = value - old
                    if delta < 1:
                        continue

                    progressbar.update(delta)

                    old = value

    return ProgressHandler


def file_size_mb(fname):
    return os.stat(fname).st_size / 1024 / 1024.


def convert(input_file, output_file, profile):
    streams = ffprobe('-show_streams', input_file).get('streams')

    log.info("Found %d streams.", len(streams))
    log.debug("\n%s", pformat(streams))

    progress_server = SocketServer.TCPServer(
        ('', 0),
        create_handler(streams[0].duration * 1000000)
    )

    thread = Thread(target=progress_server.serve_forever)
    thread.daemon = True
    _, progress_port = progress_server.server_address

    thread.start()

    args = (
        '-progress',
        'tcp://localhost:{0}'.format(progress_port),
    )

    args += (
        '-loglevel',
        'panic',
        '-i', input_file,
        '-y',
    )

    args += tuple(profile(streams))

    args += (output_file,)

    try:
        ffmpeg(*args)

        input_file_size = file_size_mb(input_file)
        output_file_size = file_size_mb(output_file)
        ratio = float(output_file_size)/float(input_file_size)

        log.info(
            "File optimized:\n\tOriginal size: %02fMb\n\tNew size: %02fMb\n\tRatio: %03f",
            input_file_size,
            output_file_size,
            ratio,
        )
    finally:
        progress_server.server_close()

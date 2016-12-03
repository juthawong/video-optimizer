#!/usr/bin/env python
from __future__ import division
import os
import logging
from argparse import ArgumentParser
from video_optimizer import PIDFile
from video_optimizer.commands import convert
from video_optimizer.profiles import profile_options, select_profile

logging.getLogger('sh').setLevel(logging.WARNING)

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", 'info').upper(), logging.INFO),
    format=u"[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s %(message)s"
)

log = logging.getLogger(__name__)

parser = ArgumentParser()
parser.add_argument("input_file", help="Input file")
parser.add_argument("-o", "--output-file", help="Output file (until recursive)")
parser.add_argument("--replace", action="store_true", default=False, help="Replace original")
parser.add_argument("-P", "--pid-file", default="/tmp/video-optimizer.pid")
parser.add_argument("-p", "--profile", default="apple")

profile_options(parser)


def run():
    options = parser.parse_args()
    try:
        with PIDFile(options.pid_file):
            options.profile = select_profile(options.profile, options)

            if not options.output_file:
                fname = os.path.splitext(options.input_file)[0]
                options.output_file = "%s.mp4" % fname

            options.input_file = options.input_file.decode('utf-8')
            options.output_file = options.output_file.decode('utf-8')

            convert(options.input_file, options.output_file, options.profile)

            if options.replace:
                os.remove(options.input_file)

            exit(0)
    except Exception as e:
        log.exception(e)
        exit(128)


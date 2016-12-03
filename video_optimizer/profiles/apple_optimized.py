#!/usr/bin/env python
# encoding: utf-8
import operator
import logging
from video_optimizer import humanize
from video_optimizer.profiles import BaseProfile, register


log = logging.getLogger(__name__)


@register
class AppleOptimized(BaseProfile):
    def arguments(self, streams):
        result = (
            '-map_metadata', '0',
        )

        video_stream = next(iter(filter(lambda x: x.codec_type == 'video', streams)))
        audio_stream = list(filter(lambda x: x.codec_type == 'audio', streams))

        fps = operator.truediv(*tuple(map(int, video_stream.avg_frame_rate.split("/"))))

        log.info("Current bitrate: %s", humanize(video_stream.bit_rate, 'b/s'))

        result_bitrate = self.bitrate or video_stream.bit_rate * self.loose_factor
        log.info("Result bitrate: %s", humanize(result_bitrate, "b/s"))

        result += (
            '-map', '0:{0}'.format(video_stream['index']),
        )

        if audio_stream:
            audio_stream = audio_stream[0]
            result += (
                '-map', '0:{0}'.format(audio_stream['index']),
                '-ar', 44100,
                '-c:a', 'aac',
                '-b:a', '%sk' % (self.audio_bitrate_stereo if audio_stream.channels > 1 else self.audio_bitrate_mono),
            )
        else:
            result += ('-an',)


        if self.copy_data_streams:
            data_streams = list(sorted(filter(lambda x: x.codec_type == 'data', streams), key=lambda x: x['bit_rate']))
        else:
            data_streams = []

        if data_streams:
            data_stream = data_streams[-1]

            log.info(data_stream)

            result += (
                '-map', "0:{0}".format(data_stream['index']),
                '-c:d', 'copy',
            )

        result += (
            '-f', 'mp4',
            '-c:d', "copy",
            '-movflags', '+faststart',
            '-bsf:v', 'h264_mp4toannexb',
            '-c:v', 'libx264',
            '-b:v', "%d" % result_bitrate,
            '-maxrate', "%d" % result_bitrate,
            '-profile:v', 'high',
            '-level', '4.2',
            '-x264opts',
            ':'.join((
                'merange=64',
                'me=umh',
                'b-pyramid=none',
                'slices=1',
                'b-adapt=0',
                'bframes=2',
                'scenecut=-1',
                'deblock',
                'keyint={keyint_max}',
                'min-keyint={keyint_min}',
                'no-scenecut',
            )).format(
                keyint_min=int(fps),
                keyint_max=int(fps * 60),
            ),
            '-preset', 'slow',
        )

        return result

    @classmethod
    def get_prefix(self):
        return 'apple'

    @classmethod
    def expose_options(self):
        return [
            {
                'name': 'loose_factor',
                'type': float,
                'default': 1.,
            },
            {
                'name': 'bitrate',
                'type': int,
                'default': None,
            },
            {
                'name': 'audio-bitrate-mono',
                'type': int,
                'default': 56,
            },
            {
                'name': 'audio-bitrate-stereo',
                'type': int,
                'default': 192,
            },
            {
                'name': 'copy_data_streams',
                'type': bool,
                'default': False,
            }
        ]

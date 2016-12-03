#!/usr/bin/env python
from setuptools import find_packages, setup


setup(
    name='video-optimizer',
    version='0.0.1',
    description="It's a simple ffmpeg-wrapper for compressing videos which makes iPhone",
    author='Dmitry Orlov',
    license="Apache 2",
    author_email='me@mosquito.su',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'video-optimizer = video_optimizer.main:run',
        ]
    },
    install_requires=(
        'sh',
        'tqdm',
    ),
)

#!/usr/bin/env python
from setuptools import find_packages, setup


setup(
    name='video-optimizer',
    version='0.1',
    description='FFMpeg helper tool',
    author='Dmitry Orlov',
    author_email='me@mosquito.su',
    packages=find_packages(),
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

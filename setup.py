#!/usr/bin/env python

from setuptools import setup

setup(
    name="django-cms-media-gallery",
    version="0.0.1",
    description="A media gallery for django-cms",
    author="Paulo Alvarado",
    author_email="commonzenpython@gmail.com",
    url="http://github.com/czpython/django-cms-media-gallery",
    packages=['cms_media_gallery'],
    dependency_links = ['https://github.com/czpython/django-uploadit/tarball/master#egg=uploadit'],
    install_requires=[
        'pylibmc',
        'django-pylibmc',
        'sorl-thumbnail',
        'django-ajax-selects',
    ],
)
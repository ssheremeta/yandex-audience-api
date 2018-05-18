#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup, find_packages

module_dir = os.path.dirname(__file__)

with codecs.open(os.path.join(module_dir, "README.rst"), encoding="utf8") as f:
    long_description = f.read()

setup(name="yaaudience",
      version="1.0.0",
      packages=find_packages(exclude=("tests",)),
      description="Yandex.Audience REST API client library",
      long_description="Yandex.Audience REST API client library",
      author="Sergey Sheremeta",
      author_email="s.w.sheremeta@gmail.com",
      license="GPLv3",
      python_requires=">=3",
      install_requires=["requests"],
      url="https://github.com/ssheremeta/yandex-audience-api",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules"],
      keywords="yandex yandex.audience rest python")

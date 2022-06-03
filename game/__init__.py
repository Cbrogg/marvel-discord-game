"""
Marvel Game API
~~~~~~~~~~~~~~~~~~~

A basic Marvel Game API.

:copyright: (c) 2015-present TonyStark&KateFuller
:license: MIT, see LICENSE for more details.

"""

__title__ = 'marvel_game'
__author__ = 'TonyStark&KateFuller'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015-present TonyStark&KateFuller'
__version__ = '0.0.1a'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging
from typing import NamedTuple, Literal

from .character import *
from .consts import *
from .enemy import *
from .enums import *
from .game import *
from .player import *
from .priority import *
from .special import *
from .utils import *
from .zombie import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=1, releaselevel='alpha', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())

del logging, NamedTuple, Literal, VersionInfo

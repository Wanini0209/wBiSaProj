"""Common definitions for invoke tasks.

This module contains common constants and configurations used across
all task modules.

Attributes
----------
VENV_PREFIX : str
    Prefix command for running commands in virtual environment.
_COMMON_TARGETS : list of str
    List of common target directories for various tasks.
COMMON_TARGETS_AS_STR : str
    Space-separated string of common targets.
SOURCE_PACKAGES : list of str
    List of source code packages for coverage checking.
USE_PTY : bool
    Whether to use pseudo-terminal based on platform.

"""

import sys

VENV_PREFIX = "pipenv run"

# 將 wutils 加入通用目標列表
_COMMON_TARGETS = ["wsatools", "wutils", "tests", "setup.py", "tasks"]
COMMON_TARGETS_AS_STR = " ".join(_COMMON_TARGETS)

# 新增：定義明確的原始碼套件列表，取代原本的 TEST_TARGET
SOURCE_PACKAGES = ["wsatools", "wutils"]

# The differences between Linux and Windows
USE_PTY = sys.platform != "win32"

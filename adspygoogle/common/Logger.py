#!/usr/bin/python
#
# Copyright 2010 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Interface for handling logging."""

__author__ = 'api.arogal@gmail.com (Adam Rogal)'

import logging
import os
import sys


class Logger(object):

  """Responsible for impementing logging.

  Allows to write to an external log or a console. There are 4 types of
  handlers denoted by the handler constants: NONE, FILE, CONSOLE, and
  FILE_AND_CONSOLE. There are also 6 verbosity levels defined by the constants:
  NOTSET, DEBUG, INFO, WARNING, ERROR, and CRITICAL. These constants are
  derived from the original logging module with CRITCAL being the highest
  importance.

  This class is a wrapper for the standard logging module.
  """

  # Handler constants.
  NONE = 0
  FILE = 1
  CONSOLE = 2
  FILE_AND_CONSOLE = 3

  # Level constants.
  CRITICAL = logging.CRITICAL
  ERROR = logging.ERROR
  WARNING = logging.WARNING
  INFO = logging.INFO
  DEBUG = logging.DEBUG
  NOTSET = logging.NOTSET

  def __init__(self, lib_sig, log_path=os.path.join(os.getcwd(), 'logs')):
    """Inits Logger.

    Args:
      lib_sig: str Signature of the client library.
      [optional]
      log_path: str Absolute or relative path to the logs directory.
    """
    self.__lib_sig = lib_sig
    self.__log_path = log_path
    self.__log_table = {}

  def __CreateLog(self, log_name, log_level=NOTSET, log_handler=FILE,
                  stream=sys.stderr):
    """Creates the log used for logging.

    Args:
      log_name: str Name of the log. If the log is handled by an external
                file, this will be the file name.
      [optional]
      log_level: str Level of the log. Should be one of CRITICAL, ERROR,
                 WARNING, INFO, DEBUG, or NOTSET.
      log_handler: int Type of log handler. Should be one of NONE, FILE,
                   CONSOLE, or FILE_AND_CONSOLE.
      stream: file Stream to send data into.
    """
    logger = logging.getLogger(log_name)

    # Update log level to reflect changes. If a higher log level is given
    # the logger should raise it's boundary.
    if log_level < logger.level or logger.level == logging.NOTSET:
      logger.setLevel(log_level)

    if (log_name in self.__log_table and
        self.__log_table[log_name] == Logger.FILE_AND_CONSOLE):
      # Don't add any more handlers.
      return

    # Create an entry for log name.
    if log_name not in self.__log_table:
      self.__log_table[log_name] = Logger.NONE

    if log_handler != Logger.NONE:
      fmt = ('[%(asctime)s::%(levelname)s::' + self.__lib_sig +
             '] %(message)s')
      # Add FILE handler if needed.
      if (log_handler == Logger.FILE or
          log_handler == Logger.FILE_AND_CONSOLE and
          self.__log_table[log_name] != Logger.FILE):
        if not os.path.exists(self.__log_path):
          os.makedirs(self.__log_path)
        fh = logging.FileHandler(os.path.join(self.__log_path,
                                              '%s.log' % log_name))
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter(fmt))
        logger.addHandler(fh)
        # Binary arithmetic to yield updated handler.
        self.__log_table[log_name] = self.__log_table[log_name] + Logger.FILE

      # Add CONSOLE handler if needed.
      if (log_handler == Logger.CONSOLE or
          log_handler == Logger.FILE_AND_CONSOLE and
          self.__log_table[log_name] != Logger.CONSOLE):
        ch = logging.StreamHandler(stream)
        ch.setLevel(log_level)
        ch.setFormatter(logging.Formatter(fmt))
        logger.addHandler(ch)
        # Binary arithmetic to yield updated handler.
        self.__log_table[log_name] = self.__log_table[log_name] + Logger.CONSOLE

  def Log(self, log_name, message, log_level=NOTSET, log_handler=FILE):
    """Log message to an external file.

    Args:
      log_name: str Name of the log. If the log is handled by an external
                file, this will be the file name appended by log.
      message: str Message to log.
      [optional]
      log_level: int Level of importance of the current message. Not
                 supplying this parameter will cause the logger to log at the
                 lowest level of its handlers. If a handler has cut-off higher
                 than this lowest level, the message will be ignored by that
                 handler.
      log_handler: int Type of log handler. Should be one of NONE, FILE,
                   CONSOLE, or FILE_AND_CONSOLE.
    """
    logger = logging.getLogger(log_name)

    # Instantiate handlers for logger with default values if none exists.
    if not logger.handlers:
      self.__CreateLog(log_name, log_level, log_handler)

    if log_level == Logger.NOTSET:
      logger.log(logger.getEffectiveLevel(), message)
    else:
      logger.log(log_level, message)

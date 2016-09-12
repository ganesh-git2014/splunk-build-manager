'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/15/16
'''
import logging
import os
from abc import ABCMeta
from logging.handlers import RotatingFileHandler

_CURRENT_DIR = os.path.dirname(__file__)

_LOG_FORMAT = '[%(asctime)s] %(levelname)s - %(name)s: %(message)s'
_FILE_NAME = os.path.join(_CURRENT_DIR, "splunk-build-manager.log")


def setup_logger(debug=False):
    """
    Setups up the logging library

    @param debug: If debug log messages are to be outputted
    @type debug: bool
    """
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    hdlr = RotatingFileHandler(filename=_FILE_NAME, mode='w', maxBytes=500000, backupCount=2)
    fmt = logging.Formatter(_LOG_FORMAT)
    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)
    logging.root.setLevel(level)
    # Disable some unnecessary logs.
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)


class Logging(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._logger = self._get_logger()
        super(Logging, self).__init__()

    def _get_logger(self):
        '''
        Creates a new logger for this instance, should only be called once.

        @return: The newly created logger.
        '''
        return logging.getLogger(self._logger_name)

    @property
    def _logger_name(self):
        '''
        The name of the logger.

        @rtype: str
        '''
        return self.__class__.__name__

    @property
    def logger(self):
        '''
        The logger of this Splunk object.

        @return: The associated logger.
        '''
        return self._logger


def get_logger(name):
    return logging.getLogger(name)


setup_logger()

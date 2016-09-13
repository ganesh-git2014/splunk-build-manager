#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 9/1/16
"""
import copy
import os

from twisted.web import server
from twisted.internet import reactor

from customise_resource import CustomiseFile
from logging_base import get_logger
from settings import STATIC_RESOURCE_PATH
from twisted.web import resource


_LOGGER = get_logger('WebServer')


def hackGetResourceFor(self, request):
    """
    Hack the getResourceFor function to log the site visit info.
    """
    request.site = self
    if (not request.uri.startswith('/static')) and (not request.uri.endswith('/')):
        _LOGGER.info('Request for uri: {0} from {1}'.format(request.uri, request.client.host))
    request.sitepath = copy.copy(request.prepath)
    return resource.getChildForRequest(self.resource, request)


server.Site.getResourceFor = hackGetResourceFor


class CustomiseServer(object):
    def __init__(self, static_file_path, port=8080):
        """
        :param static_resource_path: The dir that you put the css and js files. Should be full path.
        """
        self.static_file_path = static_file_path
        self.port = port

    def run(self):
        """
        :param static_file_path: The dir you want to display all the files in it on the web page.
        :param port: Web server port.
        """
        resource = CustomiseFile(self.static_file_path)
        resource.putChild(STATIC_RESOURCE_PATH.split(os.sep)[-1], CustomiseFile(STATIC_RESOURCE_PATH))
        site = server.Site(resource)
        reactor.listenTCP(self.port, site)
        reactor.run()

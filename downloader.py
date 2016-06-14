'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/14/16
'''
from helmut.splunk_package import NightlyPackage


class Downloader(object):

    def __init__(self):
        pass

    def download_package(self, branch, build, package_type):
        pkg = NightlyPackage(branch=branch, build=build, package_type=package_type)
        url = pkg.get_url()

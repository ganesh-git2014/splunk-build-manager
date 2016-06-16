'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/14/16
'''
import os
import requests
import hashlib
import time
from settings import MAX_DOWNLOAD_TRY

from logging_base import Logging


class BuildDownloader(Logging):
    def __init__(self, dir_path, platform_package, branch=None, build=None, package_type=None):
        """
        :param file_path: The target download directory.
        :param branch: default is current branch.
        :param build: default is latest build.
        :param package_type: default is splunk.
        """
        super(BuildDownloader, self).__init__()
        self.platform_package = platform_package
        self.branch = branch if branch else 'current'
        self.build = build if build else 'latest'
        self.package_type = package_type if package_type else 'splunk'
        self.dir_path = dir_path

    def download_package(self):
        """
        Download the package and check its md5 check sum.
        :return: True if download successfully.
        """
        url = self._get_url_from_splunk_build_fetcher()
        file_name = url.split('/')[-1]
        file_path = os.path.join(self.dir_path, file_name)
        # Return if already downloaded.
        if os.path.isfile(file_path):
            return True
        # Make dir folder if not exist.
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)
        with open(file_path, mode='w') as f:
            self.download_from_url(url, f)
        check_sum = self.get_md5(url)
        if self.check_md5(file_path, check_sum):
            return True
        else:
            os.remove(file_path)
            return False

    def _get_url_from_splunk_build_fetcher(self):
        '''
        Returns the URL for the specified package using splunk_build_fetcher script.

        @return: The URL.
        @rtype: str
        '''
        rURL = 'http://releases.splunk.com/'
        tURI = 'cgi-bin/splunk_build_fetcher.py?'

        # TODO: temp solution for hunk beta not available on splunk_build_fetcher.
        if self.package_type == 'hunkbeta':
            tURI = 'cgi-bin/build_fetcher.py?'

        pTag = 'PLAT_PKG='
        dTag = 'DELIVER_AS=url'
        vTag = 'VERSION='
        cTag = 'P4CHANGE='
        bTag = 'BRANCH='
        productTag = 'PRODUCT='
        ufTag = 'UF='

        # handle UNIVERSAL_FORWARDER differently because in splunk_build_fetcher
        # there is no product named UNIVERSAL_FORWARDER.
        if self.package_type == 'universalforwarder':
            url = ''.join((rURL, tURI, dTag,
                           '&', pTag, self.platform_package,
                           '&', bTag, self.branch,
                           '&', ufTag, '1'))
        else:
            url = ''.join((rURL, tURI, dTag,
                           '&', productTag, self.package_type,
                           '&', pTag, self.platform_package,
                           '&', bTag, self.branch))

        if self.build != 'latest':
            url += '&' + cTag + str(self.build)

        self.logger.debug("Get url from splunk build fetcher: %s" % url)

        for i in range(12):
            try:
                response = requests.get(url)
                assert response.status_code == 200
                return response.content.rstrip()
            except Exception, e:
                self.logger.warn('Get url failed. Retry after 5 seconds.')
                time.sleep(5)
        else:
            raise Exception("Get url failed after 60s.")

    def download_from_url(self, url, file_object):
        # NOTE the stream=True parameter
        response = requests.get(url, stream=True)
        assert response.status_code == 200
        self.logger.info('Start downloading from {0}'.format(url))
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                file_object.write(chunk)
                file_object.flush()
                os.fsync(file_object.fileno())  # make sure all internal buffers are written to disk
        return True

    def get_md5(self, url):
        md5_url = url + '.md5'
        response = requests.get(md5_url)
        return response.content.split(' ')[-1]

    def check_md5(self, file_path, check_sum):
        m = hashlib.md5()
        blocksize = 2 ** 20
        with open(file_path, "rb") as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                m.update(buf)
        return m.hexdigest() == check_sum

    def start_download(self):
        count = 0
        package_info = str((self.package_type, self.branch, self.build, self.platform_package))
        while True:
            if self.download_package():
                self.logger.info('Download package {0} successfully.'.format(package_info))
                break
            count += 1
            self.logger.warning('Download package {0} failed {1} times, try again...'.format(package_info, count))
            if count > MAX_DOWNLOAD_TRY:
                self.logger.error('Download package {0} failed, just give up.'.format(package_info))
                break


if __name__ == '__main__':
    downloader = BuildDownloader('/tmp/builds/current/', 'x64-release.msi')
    downloader.start_download()

'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/14/16
'''
import os
import requests
import hashlib
import time
from requests.adapters import HTTPAdapter
from settings import MAX_DOWNLOAD_TRY
from logging_base import Logging
from settings import MAX_CONCURRENT_THREADS, RECORD_DOWNLOAD_SPEED, RECORD_DOWNLOAD_INTERVAL

_SESSION = requests.session()
_SESSION.mount('http', HTTPAdapter(pool_maxsize=2 * MAX_CONCURRENT_THREADS))


class BuildDownloader(Logging):
    def __init__(self, dir_path, platform_package, branch=None, build=None, package_type=None):
        """
        :param file_path: The target download directory.
        :param branch: default is current branch.
        :param build: default is latest build.
        :param package_type: default is splunk.
        """
        self.platform_package = platform_package
        self.branch = branch if branch else 'current'
        self.build = build if build else 'latest'
        self.package_type = package_type if package_type else 'splunk'
        self.dir_path = dir_path
        self._downloaded_size = 0
        self._record_time = 0
        super(BuildDownloader, self).__init__()

    @property
    def _logger_name(self):
        return self.__class__.__name__ + '({0}-{1}-{2}-{3})'.format(self.package_type, self.branch, self.build,
                                                                    self.platform_package)

    def download_package(self):
        """
        Download the package and check its md5 check sum.
        :return: True if download successfully.
        """
        url = self._get_url_from_splunk_build_fetcher()
        file_name = url.split('/')[-1]
        file_path = os.path.join(self.dir_path, file_name)
        tmp_path = os.path.join('/tmp', file_name)
        # Return if already downloaded.
        if os.path.isfile(file_path):
            self.logger.info('Package exists already, skip downloading.')
            return True
        # Make dir folder if not exist.
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)
        # Must open the destination file in binary mode to ensure python doesn't try and translate newlines for you.
        with open(tmp_path, mode='wb') as f:
            try:
                self.download_from_url(url, f)
            except Exception, e:
                self.logger.error('Exception during download: {0}'.format(e.message))
                os.remove(tmp_path)
                return False
        check_sum = self.get_md5(url)
        if self.check_md5(tmp_path, check_sum):
            os.rename(tmp_path, file_path)
            self.logger.info('Download package successfully.')
            return True
        else:
            os.remove(tmp_path)
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
        response = _SESSION.get(url, stream=True)
        assert response.status_code == 200
        self.logger.info('Start downloading from {0}'.format(url))
        chunk_size = 1024
        for chunk in response.iter_content(chunk_size=chunk_size):
            if RECORD_DOWNLOAD_SPEED:
                self.record_download_speed(chunk_size)
            if chunk:  # filter out keep-alive new chunks
                file_object.write(chunk)
                file_object.flush()
                os.fsync(file_object.fileno())  # make sure all internal buffers are written to disk
        return True

    def record_download_speed(self, chunk_size):
        now = time.time()
        if self._record_time < now:
            self.logger.info('Downloading {0}kb/s'.format(self._downloaded_size / 1024 / RECORD_DOWNLOAD_INTERVAL))
            self._record_time = now + RECORD_DOWNLOAD_INTERVAL
            self._downloaded_size = 0
        else:
            self._downloaded_size += chunk_size

    def get_md5(self, url):
        md5_url = url + '.md5'
        response = requests.get(md5_url)
        check_sum = response.content.split(' ')[-1].rstrip()
        self.logger.debug('Get md5 check sum [{0}] from url.'.format(check_sum))
        return check_sum

    def check_md5(self, file_path, check_sum):
        m = hashlib.md5()
        block_size = 2 ** 20
        with open(file_path, "rb") as f:
            while True:
                buf = f.read(block_size)
                if not buf:
                    break
                m.update(buf)
        file_check_sum = m.hexdigest()
        if file_check_sum != check_sum:
            self.logger.warning(
                'The expect check sum is {0} while the downloaded file\'s check sum is {1}.'.format(check_sum,
                                                                                                    file_check_sum))
        return file_check_sum == check_sum

    def start_download(self):
        count = 0
        while True:
            if self.download_package():
                break
            count += 1
            if count > MAX_DOWNLOAD_TRY:
                self.logger.error('Download package failed, just give up.')
                break
            else:
                self.logger.warning('Download package failed {0} times, try again...'.format(count))


if __name__ == '__main__':
    downloader = BuildDownloader('/tmp/builds/ace/', 'x64-release.msi', branch='ace')
    downloader.start_download()

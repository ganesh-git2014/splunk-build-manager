'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/14/16
'''
import os
import requests
import hashlib
from helmut.splunk_package import NightlyPackage
from settings import MAX_DOWNLOAD_TRY

from logging_base import Logging


class BuildDownloader(Logging):
    def __init__(self, dir_path, branch=None, build=None, package_type=None):
        """
        :param file_path: The target download directory.
        :param branch: default is current branch.
        :param build: default is latest build.
        :param package_type: default is splunk.
        """
        super(BuildDownloader, self).__init__()
        self.branch = branch
        self.build = build
        self.package_type = package_type
        self.dir_path = dir_path

    def download_package(self):
        """
        Download the package and check its md5 check sum.
        :return: True if download successfully.
        """
        pkg = NightlyPackage(branch=self.branch, build=self.build, package_type=self.package_type)
        url = pkg.get_url()
        file_name = url.split('/')[-1]
        file_path = os.path.join(self.dir_path, file_name)
        # Make dir folder if not exist.
        if not os.path.isdir(self.dir_path):
            os.makedirs(self.dir_path)
        with open(file_path, mode='w') as f:
            self.download_from_url(url, f)
        check_sum = self.get_md5(url)
        return self.check_md5(file_path, check_sum)

    def download_from_url(self, url, file_object):
        # NOTE the stream=True parameter
        response = requests.get(url, stream=True)
        assert response.status_code == 200
        for chunk in response.iter_content(chunk_size=16 * 1024):
            if chunk:  # filter out keep-alive new chunks
                file_object.write(chunk)
                # os.fsync(file_object.fileno())  # make sure all internal buffers are written to disk
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

    def start(self):
        count = 0
        while not self.download_package():
            count += 1
            self.logger.warning('Download package failed {0} times, try again...'.format(count))
            if count > MAX_DOWNLOAD_TRY:
                self.logger.error('Download package failed, just give up.')
                break


if __name__ == '__main__':
    downloader = BuildDownloader('/tmp')
    downloader.start()

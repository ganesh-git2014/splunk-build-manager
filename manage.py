'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/15/16
'''
import os
import operator
import re
import requests
import time
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from download import BuildDownloader
from logging_base import Logging
from settings import MAX_CONCURRENT_THREADS, PLATFORM_PACKAGES, FILTER_BRANCH_REGEX, MUST_DOWNLOAD_BRANCH, EXPIRE_DAYS


class BuildManager(Logging):
    def __init__(self, root_path):
        """
        :param root_path: The root dir path to save the downloaded builds.
        """
        super(BuildManager, self).__init__()
        self.branch_list = self._get_branch_list()
        self.root_path = root_path

    def _get_branch_list(self):
        """
        Acquire the branch list of splunk from http://releases.splunk.com/.
        """
        response = requests.get('http://releases.splunk.com/status.html')
        parsed_html = BeautifulSoup(response.content, 'html.parser')
        branch_list = []
        for tag in parsed_html.find_all('center'):
            if tag.string:
                if tag.string.startswith('Branch: '):
                    branch_list.append(tag.string.replace('Branch: ', ''))
        return self._filter_branches(branch_list)

    def _filter_branches(self, branch_list):
        filtered_branches = []
        for branch in branch_list:
            for pattern in FILTER_BRANCH_REGEX:
                if re.match(pattern, branch):
                    break
            else:
                filtered_branches.append(branch)

        for branch in MUST_DOWNLOAD_BRANCH:
            if not branch in filtered_branches:
                filtered_branches.append(branch)
        return filtered_branches

    def download_latest_builds(self):
        self.logger.info('Start downloading latest builds of these branch: {0}'.format(str(self.branch_list)))
        results = []
        thread_pool = ThreadPool(processes=MAX_CONCURRENT_THREADS)
        for branch in self.branch_list:
            for platform_pkg in PLATFORM_PACKAGES:
                downloader = BuildDownloader(os.path.join(self.root_path, branch), platform_pkg, branch=branch)
                results.append(thread_pool.apply_async(downloader.start_download))

        for result in results:
            msg = result.get()
            if msg:
                self.logger.error(msg)
        self.logger.info('All download threads end.')

    def delete_expire_builds(self):
        expire_time = time.time() - EXPIRE_DAYS * 3600 * 24
        delete_files = []
        for root, dirs, files in os.walk(self.root_path):
            create_times = dict()
            for f in files:
                if not f.startswith('.'):
                    platform_pkg = '-'.join(f.split('-')[3:])
                    if not platform_pkg in create_times:
                        create_times[platform_pkg] = dict()
                    file_path = os.path.join(root, f)
                    create_times[platform_pkg][file_path] = os.path.getctime(file_path)
            for platform_pkg in create_times.keys():
                sorted_pairs = sorted(create_times[platform_pkg].items(), key=operator.itemgetter(1))
                # Will delete the package if it is expired and not the only one file (of that platform) in that folder.
                for file_path, ct in sorted_pairs[:-1]:
                    if ct < expire_time:
                        delete_files.append(file_path)

        for file_path in delete_files:
            os.remove(file_path)
            self.logger.info('{0} is deleted due to expiration.'.format(file_path))


if __name__ == '__main__':
    manager = BuildManager('/tmp/builds/')
    # manager.download_latest_builds()
    manager.delete_expire_builds()

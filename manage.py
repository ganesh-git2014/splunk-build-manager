'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/15/16
'''
import os

import re
import requests
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from download import BuildDownloader
from logging_base import Logging
from settings import MAX_CONCURRENT_THREADS, PLATFORM_PACKAGES, FILTER_BRANCH_REGEX, MUST_DOWNLOAD_BRANCH


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

    def download_builds(self):
        results = dict()
        thread_pool = ThreadPool(processes=MAX_CONCURRENT_THREADS)
        for branch in self.branch_list:
            for platform_pkg in PLATFORM_PACKAGES:
                downloader = BuildDownloader(os.path.join(self.root_path, branch), platform_pkg, branch=branch)
                results[branch] = thread_pool.apply_async(downloader.start)

        for branch in self.branch_list:
            print results[branch].get()

    def delete_builds(self):
        pass


if __name__ == '__main__':
    manager = BuildManager('/tmp/builds/')
    manager.download_builds()

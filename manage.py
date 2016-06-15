'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/15/16
'''
import os

import requests
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
from download import BuildDownloader
from logging_base import Logging
from settings import MAX_CONCURRENT_THREADS


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
        return branch_list

    def download_builds(self):
        results = dict()
        thread_pool = ThreadPool(processes=MAX_CONCURRENT_THREADS)
        for branch in self.branch_list:
            downloader = BuildDownloader(os.path.join(self.root_path, branch), branch=branch)
            results[branch] = thread_pool.apply_async(downloader.start)

        for branch in self.branch_list:
            print results[branch].get()


if __name__ == '__main__':
    manager = BuildManager('/tmp')
    manager.download_builds()

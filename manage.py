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
from settings import MAX_CONCURRENT_THREADS, PLATFORM_PACKAGES, FILTER_BRANCH_REGEX, MUST_DOWNLOAD_BRANCH, EXPIRE_DAYS, \
    NEVER_DELETE_BRANCH, RESERVE_RC_BUILDS

_SESSION = requests.session()
_BASE_URL = 'http://releases.splunk.com'
_RELEASE_URL = 'http://releases.splunk.com/status.html'


class BuildManager(Logging):
    def __init__(self, root_path):
        """
        :param root_path: The root dir path to save the downloaded builds.
        """
        super(BuildManager, self).__init__()
        self.root_path = root_path
        self._cache = dict()
        self.branch_list = self._get_branch_list()
        if RESERVE_RC_BUILDS:
            self.rc_builds = self._get_rc_list()
        else:
            self.rc_builds = dict()

    def _get_branch_list(self):
        """
        Acquire the branch list of splunk from http://releases.splunk.com/.
        """
        response = _SESSION.get(_RELEASE_URL)
        self._cache['release_page'] = response.content
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

    def _get_rc_list(self):
        rc_builds = dict()
        release_page = self._cache.get('release_page')
        if not release_page:
            release_page = _SESSION.get(_RELEASE_URL).content
        parsed_html = BeautifulSoup(release_page, 'html.parser')
        for tag in parsed_html.find_all('tr', {'bgcolor': '#54C944'}):
            branch = tag.contents[0].text
            if branch in self.branch_list:
                link = tag.contents[1].find('a').attrs['href']
                download_page = _SESSION.get(_BASE_URL + '/' + link).content
                build_number = self._get_commit_number(download_page)
                label = tag.contents[2].text
                rc_builds[label] = (branch, build_number)
        return rc_builds

    def _get_commit_number(self, download_page):
        parsed_html = BeautifulSoup(download_page, 'html.parser')
        for tag in parsed_html.find_all('a'):
            href = tag.attrs['href']
            if href.endswith(PLATFORM_PACKAGES[0]):
                return href[:-len(PLATFORM_PACKAGES[0])].split('-')[-2]

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
        never_delete_folders = [os.path.join(self.root_path, branch) for branch in NEVER_DELETE_BRANCH]
        rc_builds = [rc[1] for rc in self.rc_builds.values()]
        expire_time = time.time() - EXPIRE_DAYS * 3600 * 24
        delete_files = []
        for root, dirs, files in os.walk(self.root_path):
            if root in never_delete_folders:
                continue
            create_times = dict()
            for f in files:
                if not f.startswith('.'):
                    build_number = f.split('-')[2]
                    if build_number in rc_builds:
                        continue
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

        self.logger.info('All expired files are deleted.')


if __name__ == '__main__':
    manager = BuildManager('/tmp/splunk_builds')
    # manager.download_latest_builds()
    manager.delete_expire_builds()

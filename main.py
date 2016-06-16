'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/14/16
'''
from multiprocessing.pool import ThreadPool
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from manage import BuildManager
from settings import ROOT_DIR


def main():
    pool = ThreadPool(processes=1)
    lc = LoopingCall(manage_build)
    pool.apply_async(lc.start, (3600 * 2,))
    resource = File(ROOT_DIR)
    factory = Site(resource)
    reactor.listenTCP(8080, factory)
    reactor.run()


def manage_build():
    manager = BuildManager(ROOT_DIR)
    manager.download_latest_builds()
    manager.delete_expire_builds()


if __name__ == '__main__':
    main()

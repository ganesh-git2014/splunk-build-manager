'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/14/16
'''
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from manage import BuildManager


def main():
    lc = LoopingCall(manage_build)
    lc.start(3600 * 2)
    resource = File('/tmp')
    factory = Site(resource)
    reactor.listenTCP(8080, factory)
    reactor.run()


def manage_build():
    manager = BuildManager('/root/splunk_builds')
    manager.download_latest_builds()
    manager.delete_expire_builds()


if __name__ == '__main__':
    main()

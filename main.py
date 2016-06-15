'''_
@author: Curtis Yu
@contact: cuyu@splunk.com
@since: 6/14/16
'''
from manage import BuildManager

def main():
    manager = BuildManager('/root/splunk_builds')
    manager.download_latest_builds()
    manager.delete_expire_builds()

if __name__ == '__main__':
    main()

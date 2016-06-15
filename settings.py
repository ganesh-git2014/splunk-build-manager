# Max try number of downloading builds if not successful.
MAX_DOWNLOAD_TRY = 5

# Max number of concurrent threads when downloading builds.
MAX_CONCURRENT_THREADS = 2

# The platforms of the downloaded builds.
# Refer to the build fetcher from http://releases.splunk.com/
PLATFORM_PACKAGES = ['Linux-x86_64.tgz',
                     'x64-release.msi']

# The package downloaded before these days will be deleted unless it is the only one in that folder.
EXPIRE_DAYS = 3

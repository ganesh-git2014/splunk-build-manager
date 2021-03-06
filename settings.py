# Will download builds under this directory.
ROOT_DIR = '/root/splunk_builds'

# Max try number of downloading builds if not successful.
MAX_DOWNLOAD_TRY = 5

# Max number of concurrent threads when downloading builds.
MAX_CONCURRENT_THREADS = 5

# The platforms of the downloaded builds.
# Refer to the build fetcher from http://releases.splunk.com/
PLATFORM_PACKAGES = ['Linux-x86_64.tgz',
                     'x64-release.msi',
                     'darwin-64.tgz']

# Branch name in the following will must be downloaded even if it matches the FILTER_BRANCH_REGEX.
MUST_DOWNLOAD_BRANCH = []

# Branch name matches the following regex will not be downloaded.
FILTER_BRANCH_REGEX = ['.*-.*',
                       '.*_.*',
                       'saml',
                       'shpoolnext',
                       'statestore',
                       'jsdoc',
                       'hunk',
                       'jsdoc',
                       '\d+\.',
                       'develop',
                       'cloud']

# The package downloaded before these days will be deleted unless it is the only one in that folder.
EXPIRE_DAYS = 3

# If True, will check and record download speed in the logs, this could affect the effectiveness of the program.
RECORD_DOWNLOAD_SPEED = True

# The interval (seconds) between two records of download speed.
RECORD_DOWNLOAD_INTERVAL = 30

# The interval (hours) between two download processes start.
FETCH_INTERVAL = 2

# The port of the twisted web server.
WEB_SERVER_PORT = 8080

# Packages in this folder will never be deleted due to expiration.
NEVER_DELETE_BRANCH = ['manual-build']

# If True, all RC builds of the satisfied branches will reserved forever.
RESERVE_RC_BUILDS = True
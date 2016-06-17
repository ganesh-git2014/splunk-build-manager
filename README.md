# Splunk Build Manager

This program is meant to download and manage the builds of splunk. It will implement these functions:

- Download the latest builds of given versions
- Delete the builds which are out of date (e.g. the builds downloaded 7 days ago)
- Maintain the specific builds forever (used for checking regression bugs)

## User Guide

### Prerequisites

These python libs are needed:  `requests`, `beautifulSoup4`, `twisted`

(Please make sure these libs are installed on the default python of the environment variables.)

### Deploy

Just go to the project's root directory and type:

```shell
./splunkbmd start
```

To stop[^1] the service, type:

```shell
./splunkbmd stop
```

[^1]: This will simply kill the process.

### Settings

Just see `settings.py`.

## Todo

- ~~Should not expose the file in downloading process on the web server~~
- Make download more stable (why so many incomplete downloaded packages?)
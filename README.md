# Splunk Build Manager

This program is meant to download and manage the builds of splunk. It will implement these functions:

- Download the latest builds of given versions
- Delete the builds which are out of date (e.g. the builds downloaded 7 days ago)
- Maintain the specific builds forever (used for checking regression bugs)

The web server uses [twisted](https://twistedmatrix.com), enhanced by [twisted-customise-file-server](https://github.com/cuyu/twisted-customise-file-server).

## User Guide

### Prerequisites

These python libs are needed:  `requests`, `beautifulSoup4`, `twisted`, `Jinja2`

Install them by:

```bash
pip install -r requirements.txt 
```

### Deploy

Just go to the project's root directory and type:

```bash
./splunkbmd start
```

Then the web server will be opened on http://your_server_hostname:8080 (the port number can be modified in `settings.py`) and will fetch splunk packages every two hours (by default).

---

To stop[^1] the service, type:

```shell
./splunkbmd stop
```

[^1]: This will simply kill the process.

### Settings

Just see `settings.py`.

## Todo

- ~~Should not expose the file in downloading process on the web server~~
- ~~Make download more stable~~ (It seems open too many download threads (connections) will make it unstable)
- ~~Record the download stats in the log~~
- Add a search bar in the web page (search the build in the site, if not exist get the corresponding url from http://releases.splunk.com)
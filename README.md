# Splunk Build Manager

This program is meant to download and manage the builds of splunk. It will implement these functions:

- Download the latest builds of given versions
- Delete the builds which are out of date (e.g. the builds downloaded 7 days ago)
- Maintain the specific builds forever (used for checking regression bugs)

## User Guide

### Prerequisites

These python libs are needed:  `requests`, `beautifulSoup4`, `twisted`

### Deploy

Just go to the project's root directory and type:

```shell
python main.py
```

### Settings

Just see `settings.py`.

## Todo

- ~~Should not expose the file in downloading process on the web server~~
- Make download more stable (why so many incomplete downloaded packages?)
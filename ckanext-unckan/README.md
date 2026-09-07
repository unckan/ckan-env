[![Tests](https://github.com/unckan/ckan-env/workflows/Test%20Build/badge.svg?branch=main)](https://github.com/unckan/ckan-env/actions)

# CKAN unckan extension

CKAN extension to track users activities on the site through the CKAN API.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.10            | Yes           |
| 2.11            | Yes           |


## Server terminal (read-only log viewer)

Sysadmins can open `/admin/server-terminal` to inspect configured server logs.
The page never executes shell commands. Log files must be explicitly allowlisted
with a comma-separated list of paths or glob patterns:

```ini
ckanext.unckan.server_terminal.log_paths = /var/log/supervisor/*.log, /var/log/ckan/*.log
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)

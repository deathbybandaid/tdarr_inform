# tdarr_inform

This is a program that bridges the divide between Sonarr/Radarr/Whisparr and Tdarr.
Typically Tdarr operates by filesystem events, as well as periodic disk scanning.
This program takes information from Sonarr/Radarr/Whisparr and "Informs" Tdarr of new/changed/deleted files.

If you enjoy the code, consider buying me a Coke!

<a href="https://www.paypal.com/donate?business=KEGJAGZK4NHWJ&currency_code=USD"
target="_blank">
<img src="https://www.paypalobjects.com/en_US/GB/i/btn/btn_donateCC_LG.gif" alt="PayPal this"
title="PayPal – The safer, easier way to pay online!" border="0" />
</a>

## Usage

There are 4 ways to use this program.

* The original way uses the Custom Script functionality of Sonarr/Radarr/Whisparr.
* You can also run it via CLI, but this is mostly for testing, and I haven't documented this yet.
* The NEW MODE is to run it with the `--mode server` argument.
* You can use this within Docker where it automatically runs in Server Mode.

> [!NOTE]
> Sonarr/Radarr/Whisparr file paths must be accessible to Tdarr. This script does not currently "translate" paths. This may be added in the future.

## Installation

1) Download the script
2) install python3 and python3-pip
3) Install the Python requirements `pip3 install -r requirements.txt`
4) Generate a config file using `python3 tdarr_inform.py --setup`
5) Modify your `[tdarr]/address` in `config.ini`

For Standalone, you are done. For server mode

### Server Mode

1) Go to Settings/Connect
2) Add
3) Webhook
4) Select Import,Upgrade,Rename,Delete(multiple versions of delete)
5) Set your ip-address/hostname, port 5004 with a path of /api/events
  `http://tdarr-inform.local:5004/api/events`
  `http://127.0.0.1:5004/api/events`

6) Run the program `python3 /path/to/tdarr_inform.py --mode server`
6.5) You could run it with systemd as well.
7) In a browser you can play with the web interface.

### Standalone Script

## Add to Sonarr/Radarr/Whisparr

1) Go to Settings/Connect
2) Add
3) Custom Script
4) Select Import,Upgrade,Rename,Delete(multiple versions of delete)
5) Set the path to the script

6) You might see permissions issues for the script if your sonarr user doesnt have permission to run it. `chown` it to your needs.

## Docker

This can be used in Server Mode from within Docker where it will automatically create a `/config/config.ini` file if needed. It is important to mount the config folder elsewhere so your settings don't get lost if this is updated.

The examples listed below are very basic, and will run if tdarr is also running locally. In reality you should attach to the same network as tdarr (and update the settings to point at the correct hostname etc).

### docker-compose (recommended)

```yml
services:
  tdarr_inform:
    image: ghcr.io/deathbybandaid/tdarr_inform:latest
    restart: unless-stopped
    network_mode: host
    user: "1000:1000" # This is the same as the default
    ports:
      - "5004:5004"
    volumes:
      - "/path/to/config:/config"
```

### docker cli

```sh
docker run -d \
  -p 5004:5004 \
  -v /path/to/config:/config \
  --restart unless-stopped \
  --network=host \
  ghcr.io/deathbybandaid/tdarr_inform:latest
```

## Config file

This is a copy of the file created by the `--config` option:

<details>
<summary>Default config</summary>

```ini
[logging]
level = INFO
format = None

[database]
type = sqlite
driver = None
user = None
pass = None
host = None
port = None
name = None

[main]
cache_dir = None

[tdarr_inform]
address = 0.0.0.0
port = 5004
require_auth = None
friendlyname = tdarr_inform
versions_check_interval = 10800
humanized_time_granularity = second

[tdarr]
address = localhost
port = 8265
ssl = None
accept_root_drive_path = 1

[web_ui]
theme = None
access_level = None
auto_page_refresh = 5
pages_to_refresh = None
```

</details>


## Why this exists

Tdarr is able to listen to filesystem events and/or scan the filesystem periodically.

When you store your files on a File Server or NAS, and use samba/CIFS, you lose out on filesystem events, requiring Tdarr to be dependent on frequent scans, which for large libraries can waste resources and consume a lot of time. If your applications are able to receive filesystem events, tdarr_inform may be of little help for your setup.

This tool is designed to let Sonarr/Radarr/Whisparr directly communicate with Tdarr, much like [Cloudbox/autoscan](https://github.com/Cloudbox/autoscan) is able to communicate between Sonarr/Radarr/Whisparr/Lidarr and Plex/Emby/Jellyfin.

Using tools like this allows you to reduce the file scans to 6hours/12hours/daily instead of very frequently.

Adding a direct communication between apps, allows for Tdarr to convert new media more quickly, and often prior to the media server detecting changed files. This can usually help with end-users streaming content from your media server before the content is handled by Tdarr.

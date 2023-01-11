# tdarr_inform

This is a custom script for Sonarr/Radarr/Whisparr to inform Tdarr of new/changed/deleted files without relying on filesystem events or frequent disk scanning. Bigger Explanation below.

## Installation

1) Download the script
2) install python3 and python3-pip
3) Install the Python requirements `pip3 install -r requirements.txt`
4) Generate a config file using `python3 tdarr_inform.py --setup`
5) Modify your `[tdarr]/address` in `config.ini`

## Usage

* Currently this script only works when it is added to Sonarr/Radarr/Whisparr as a Custom Script. There are some future plans that will add cli methods as well as a web service you can run on a separate machine.
* Sonarr/Radarr/Whisparr file paths must be accessible to Tdarr. This script does not currently "translate" paths. This may be added in the future.

### Standalone Script

## Add to Sonarr/Radarr/Whisparr
1) Go to Settings/Connect
2) Add
3) Custom Script
4) Select Import,Upgrade,Rename,Delete(multiple versions of delete)
5) Set the path to the script


# Why this exists

Tdarr is able to listen to filesystem events and/or scan the filesystem periodically.

When you store your files on a File Server or NAS, and use samba/CIFS, you lose out on filesystem events, requiring Tdarr to be dependent on frequent scans, which for large libraries can waste resources and consume a lot of time.

This tool is designed to let Sonarr/Radarr/Whisparr directly communicate with Tdarr, much like [Cloudbox/autoscan](https://github.com/Cloudbox/autoscan) is able to communicate between Sonarr/Radarr/Whisparr/Lidarr and Plex/Emby/Jellyfin.

Using tools like this allows you to reduce the file scans to 6hours/12hours/daily instead of very frequently.

Adding a direct communication between apps, allows for Tdarr to convert new media prior to an end-user streaming content from your media server.

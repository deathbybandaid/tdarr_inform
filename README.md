# tdarr_inform

This is is a custom script for Sonarr and Radarr to inform Tdarr of new/changed/deleted files without relying on filesystem events or frequent disk scanning. Bigger Explanation below.

To use:

0) download the script, and change the tdarr url at the top

0.5) install python3, and if the requests module doesn't come preinstalled with your install, install it through pip

1) Go to Settings/Connect
2) Add
3) Custom Script
4) Select Import,Upgrade,Rename,Delete(multiple versions of delete)
5) Set the path to the script

# Side Notes

* There is untested support for Whisparr here, but I don't download that kind of linux ISO to know
* Sonarr/Radarr/Whisparr file paths must be accessible to tdarr. This script does/will not "translate" paths.


# Why this exists

Tdarr is able to listen to filesystem events and/or scan the filesystem periodically.

When you store your files on a File Server or NAS, and use samba/CIFS, you lose out on filesystem events, requiring Tdarr to be dependent on frequent scans, which for large libraries can waste resources and consume a lot of time.

This tool is designed to let sonarr/radarr directly communicate with tdarr, much like cloudbox/autoscan is able to communicate between sonarr/radarr and plex/emby/jellyfin.

Using tools like this allows you to reduce the file scans to 6hours/12hours/daily instead of very frequently.

Adding a direct communication between apps, allows for tdarr to convert new media prior to an end-user streaming content from your media server.

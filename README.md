# tdarr_inform

This is is a custom script for Sonarr and Radarr to inform Tdarr of new/changed/deleted files without relying on filesystem events or frequent disk scanning.

To use:

0) download the script, and change the tdarr url at the top

0.5) install python3, and if the requests module doesn't come preinstalled with your install, install it through pip

1) Go to Settings/Connect
2) Add
3) Custom Script
4) Select Import,Upgrade,Rename,Delete(multiple versions of delete)
5) Set the path to the script

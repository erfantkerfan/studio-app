#!/usr/bin/bash

source /home/film/notmux.sh
sshpass -p "$(cat /etc/rsync_pass)" rsync -avhWP --no-compress --size-only /home/film/upload/media/ sftp@cdn.alaatv.com:/alaa_media/cdn/media

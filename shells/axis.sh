#!/bin/bash
source /home/film/notmux.sh
shopt -s extglob
array=( mkv MKV )
echo "Start Axis";

for f in /home/film/axis/*;
do
    if [ -d ${f} ]; then
        cd $f;
        #mkdir mp4
	for extension in "${array[@]}"; do
	        for i in *.$extension; do
	            echo $i ;
	            ffmpeg -y -i  "$i" \
	                  -metadata title="@alaa_sanatisharif" \
	                          -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 $f"/mp4/"$(basename "${i/.$extension}").mp4 -threads 23
	        done;
	done;
    fi
done;


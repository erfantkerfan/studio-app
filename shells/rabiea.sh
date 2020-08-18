#!/bin/bash
shopt -s extglob
source /home/film/notmux.sh
array=( mkv MKV mp4 MP4 flv FLV )

echo "Start Convert";

for f in /home/film/rabiea/*;
do
    if [ -d ${f} ]; then
        cd $f;
        mkdir out
        for extension in "${array[@]}"; do
              for i in *.$extension; do
                  echo $i ;
                  ffmpeg -y -i  "$i" \
                        -metadata title="@alaa_sanatisharif" \
                        -sws_flags lanczos -s 1280x720 -profile:v baseline -level 3.0 \
                              -vcodec libx264 -crf 19 -r 24 -preset ultrafast -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 128k -movflags +faststart $f"/out/"$(basename "${i/.$extension}").mp4 -threads 23
              done;
	done;
     fi
done;


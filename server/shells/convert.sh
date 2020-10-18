#!/bin/bash
shopt -s extglob
source /home/film/notmux.sh
array=( mkv MKV mp4 MP4 flv FLV )
echo "Start Convert";

for f in /home/film/convert/*;
do
    if [ -d ${f} ]; then
        cd $f;
        mkdir 240p
        mkdir hq
		for extension in "${array[@]}"; do
			for i in HD_720p/*.$extension; do
				echo $i ;
				ffmpeg -y -i  "$i" \
					-metadata title="@alaa_sanatisharif" \
					-sws_flags lanczos  -s 854x480 -profile:v baseline -level 3.0 \
							-vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 96k -movflags +faststart $f"/hq/"$(basename "${i/.$extension}").mp4 -threads 11  &
				ffmpeg -y -i  "$i" \
					-metadata title="@alaa_sanatisharif" \
					-sws_flags lanczos  -s 426x240 -profile:v baseline -level 3.0  \
							-vcodec libx264 -crf 27 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 64k -movflags +faststart $f"/240p/"$(basename "${i/.$extension}").mp4 -threads 11
			done;
		done;
    fi
done;

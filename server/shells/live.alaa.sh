#!/usr/bin/bash
while true; do
	ffmpeg -y -rtsp_transport tcp -i "rtsp://root:admin@$1/axis-media/media.amp?videocodec=h264&resolution=1280x720" -hide_banner \
          -c:v libx264 -x264opts no-scenecut -sws_flags lanczos -s:v 1280x720 -profile:v baseline -level 3.0 -tune zerolatency -preset ultrafast \
          -crf 27 -r 24 -g 48 -keyint_min 48  -c:a libfdk_aac -b:a 160k -ar 44100 -async 1 -f flv rtmp://87.107.115.29/hls/$2_720 \
          -c:v libx264 -x264opts no-scenecut -sws_flags lanczos -s:v 854x480  -profile:v baseline -level 3.0 -tune zerolatency -preset ultrafast \
		  -crf 27 -r 24 -g 48 -keyint_min 48  -c:a libfdk_aac -b:a 128k -ar 44100 -async 1 -f flv rtmp://87.107.115.29/hls/$2_480 \
          -c:v libx264 -x264opts no-scenecut -sws_flags lanczos -s:v 640x360  -profile:v baseline -level 3.0 -tune zerolatency -preset ultrafast \
		  -crf 27 -r 24 -g 48 -keyint_min 48  -c:a libfdk_aac -b:a 64k  -ar 44100 -async 1 -f flv rtmp://87.107.115.29/hls/$2_360 \
          -c:v libx264 -x264opts no-scenecut -sws_flags lanczos -s:v 426x240  -profile:v baseline -level 3.0 -tune zerolatency -preset ultrafast \
		  -crf 27 -r 24 -g 48 -keyint_min 48  -c:a libfdk_aac -b:a 64k  -ar 44100 -async 1 -f flv rtmp://87.107.115.29/hls/$2_240;
       sleep 120;
#       ffmpeg -re -i nill_720.flv \
#          -map 0 -c:a copy -c:v copy -f flv rtmp://87.107.115.29/hls/$2_720 \
#          -map 0 -c:a copy -c:v copy -f flv rtmp://87.107.115.29/hls/$2_480 \
#          -map 0 -c:a copy -c:v copy -f flv rtmp://87.107.115.29/hls/$2_360 \
#          -map 0 -c:a copy -c:v copy -f flv rtmp://87.107.115.29/hls/$2_240;
done

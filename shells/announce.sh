#echo "Start Rename";
#find /home/alaa/convert1/  -depth -exec rename "s/\s//g" {} \;
#find /home/alaa/convert1/ -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;
source /home/film/notmux.sh
echo "Start Convert";

for f in /home/film/announce/*;
do
    if [ -d ${f} ]; then
        cd $f;
        mkdir 240p
        mkdir hq
        for i in HD_720p/*.mp4; do
            echo $i ;
            ffmpeg -y -i  "$i" \
                  -metadata title="@alaa_sanatisharif" \
 	          -sws_flags lanczos -s 854x854 -profile:v baseline -level 3.0 \
                        -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 64k -movflags +faststart $f"/hq/"$(basename "${i/.mp4}").mp4 -threads 11  \
                  -sws_flags lanczos  -s 426x426 -profile:v baseline -level 3.0 \
                        -vcodec libx264 -crf 28 -r 24 -preset veryslow -pix_fmt yuv420p -tune film -acodec libfdk_aac -ab 50k -movflags +faststart $f"/240p/"$(basename "${i/.mp4}").mp4 -threads 11
        done;
    fi
done;

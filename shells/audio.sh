source /home/film/notmux.sh
echo "Start Convert";

for f in /home/film/audio/*;
do
    if [ -d ${f} ]; then
        cd $f;
        mkdir 64
        for i in 320/*.WAV; do
            echo $i ;
#            ffmpeg -y -i  "$i" \
#                  -metadata title="@alaa_sanatisharif" \
# 	          -preset veryslow -acodec libfdk_aac -ab 64k $f"/64/"$(basename "${i/.WAV}").mp3 -threads 0
            ffmpeg -y -i  "$i" \
                  -metadata title="@alaa_sanatisharif" \
                  -acodec libmp3lame -q:a 3 $f"/64/"$(basename "${i/.WAV}").mp3 -threads 23
        done;
    fi
done;


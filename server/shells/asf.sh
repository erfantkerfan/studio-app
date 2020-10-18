source /home/film/notmux.sh
echo "Start Axis";

#ffmpeg -y -i  input1.mp4 -metadata title="@alaa_sanatisharif" -preset ultrafast  -vcodec libx264 -crf 19 -r 50 -pix_fmt yuv420p -tune film -vsync 1 -async 1 out1.mp4 -threads 0
for f in /home/film/axis/*;
do
    if [ -d ${f} ]; then
        cd $f;
        mkdir mp4
        for i in *.asf; do
            echo $i ;
            ffmpeg -y -i  "$i" \
                  -metadata title="@alaa_sanatisharif" \
                          -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 $f"/mp4/"$(basename "${i/.asf}").mp4 -threads 23
        done;
        for i in *.ASF; do
            echo $i ;
            ffmpeg -y -i  "$i" \
                  -metadata title="@alaa_sanatisharif" \
                          -preset ultrafast -vcodec copy -r 50 -vsync 1 -async 1 $f"/mp4/"$(basename "${i/.ASF}").mp4 -threads 23
        done;
    fi
done;

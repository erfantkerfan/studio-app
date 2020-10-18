#-ne!/usr/bin/bash
source /home/film/notmux.sh
read -s -p "Password: " VAR1
if [[ "$VAR1" == "abc*2020" ]]; then
	sshpass -p "$(cat /etc/rsync_pass)" rsync -avhWP --no-compress --size-only /home/film/sajad/ sftp@cdn.alaatv.com:/alaa_media/cdn/paid/private
else
	echo -e "--------------- ${RED} Wrong Password! (⩾﹏⩽) ${NC}---------------"

fi
echo "$sajad_tmux_password"

#!/bin/bash

export sftp_password=$(cat /etc/rsync_pass)
while true; do

	export sftp_password=$(cat /etc/rsync_pass)

	# list of valid sessions
	array=(announce axis convert rabiea sajad upload)

	# kill any sesion that is not valid in above array
	for i in $(tmux ls | awk  '{ print $1 }' ); do
		if [[ ! " ${array[@]} " =~ "${i::-1}" ]]; then
			tmux kill-session -t "${i::-1}"
		fi
	done

	# force create the above sessions
	for i in "${array[@]}"; do
		tmux new -d -s "${i}" && tmux send -t "${i}" "cd ${i}" Enter
	done

	sleep 1
done

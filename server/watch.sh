#/bin/bash
#shopt -s extglob
trap 'kill $(jobs -p)' EXIT
if [ $# -eq 0 ]
then
        array=( axis convert upload )
        for log in "${array[@]}"
	do
                journalctl -f --no-pager -n 1000 --output=cat -u studio-$log &
        done
else
        journalctl -f --no-pager -n 1000 --output=cat -u studio-$1
fi
wait

#!/bin/bash
shopt -s extglob
if [ $# -eq 0 ]
then
        array=( axis convert upload )
        for log in "${array[@]}"
        do
                journalctl -f --no-pager -n 100 --output=cat -u studio-$log &
        done
else
        journalctl -f --no-pager -n 100 --output=cat -u studio-$1
fi
wait
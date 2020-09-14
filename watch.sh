#!/bin/bash
shopt -s extglob
array=( axis convert upload )
for log in "${array[@]}"
do
        journalctl -f --no-pager -n 100 --output=cat -u studio-$log &
done

wait
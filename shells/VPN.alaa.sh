while true; do
	ssh sohrab@proxy.alaa -p 44443 -CnNT -D 192.168.4.2:44443; sleep 3
done

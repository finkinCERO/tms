#!/bin/bash
# run as daemon
# nohup ./start.bash &>/dev/null &

service_name="service"
wsd_dir="srv/lib"
htm_dir="static"
bin_dir="srv/"
log_dir="srv/log"
ssl_dir="ssl"

echo "start service http://localhost:9393"
while :; do
   $wsd_dir/websocketd --port=9393 \
      --staticdir=$htm_dir/ \
      --dir $bin_dir \
      --loglevel=debug >>$log_dir/websocket.log
   sleep 5
done
echo "Service stopped"

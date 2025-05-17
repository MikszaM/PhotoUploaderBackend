#!/bin/bash
source noip.conf

while true; do
    if upnpc -s 2>/dev/null | grep -q "Found valid IGD"; then
        echo "Valid IGD found!"
        break
    fi
    sleep 2
done

upnpc -d 80 tcp
upnpc -d 443 tcp
upnpc -d 5900 tcp
main_ip=$(ip route get 1.1.1.1 | awk '{print $7; exit}')
upnpc -a $main_ip 80 80 tcp
upnpc -a $main_ip 443 443 tcp

upnpc -a $main_ip 5900 5900 tcp

noip-duc -g all.ddnskey.com --username $username --password $password --daemonize

cd /home/pi/PhotoUploaderBackend
/home/pi/PhotoUploaderBackend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=/etc/letsencrypt/live/weraimati.ddns.net/privkey.pem --ssl-certfile=/etc/letsencrypt/live/weraimati.ddns.net/fullchain.pem --workers 4 > /dev/null 2>&1 &

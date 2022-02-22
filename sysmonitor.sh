#!/bin/bash
clear
echo "🏥🏥🏥 Starting Health Checker Script..."
sleep 5s
echo "CPU  MEM"
while true
do
#cpuUsage=$(ps -A -o %cpu | awk '{s+=$1} END {print "" s "%"}')
cpuUsage=$(echo ""$[100-$(vmstat 1 2|tail -1|awk '{print $15}')]"")
memoryUsage=$(free | grep Mem | awk '{printf "%.1f\n", (($3/$2*100))" %"} ')
timeStamp=$(date +%s%N | cut -b1-13)
dateNow=$(date +%d.%m.%Y__%H:%M:%S)
echo -en $dateNow"| " $cpuUsage " " $memoryUsage
#printf "\x1b[1F"
curl --silent --output /dev/null -XPOST 'https://api-dev.gdeeto.com/jobs/health-check' -H 'content-type: application/json' -d '{"cpu": "'"$cpuUsage"'","mem":"'"$memoryUsage"'", "timeStamp":"'"${timeStamp}"'"}'
# https://api-dev.gdeeto.com
# https://4caf-159-224-233-85.ngrok.io
# curl --silent --output /dev/null -XPOST 'http://82.193.108.24/test' -H 'content-type: application/json' -d '{"cpu": "'"$cpuUsage"'","mem":"'"$memoryUsage"'", "timeStamp":"'"${timeStamp}"'"}'

sleep 3s
echo " "
done

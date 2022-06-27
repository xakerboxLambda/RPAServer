#!/bin/sh
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

bold=$(tput bold)
normal=$(tput sgr0)
sleep 10s
IFS=$'\n'
LocalIP=`ifconfig | awk '/inet/ && /192/ { print $(2)}'`
DayToday=`date +%d.%m.%Y__%H:%M:%S`
sleep 6s
cd /home/juan-rpa/Documents/RPAServerTest
printf "\n\n🍺🍺🍺🍺🍺🍺🍺🍺🍺🍺🍺 For ƛ Developers!\n"
printf "\n${bold}${GREEN}Hello, RPA-server will start in few seconds..."
printf "\n\nLocal IP of server is:${normal} ${RED} ${LocalIP} ${NC}"
printf  "\n${bold}${GREEN}Server started on:${normal}${RED} ${DayToday}${NC}"
cd /home/juan-rpa/Documents/RPAServerTest
sleep 1s
node ./build/index.js
#sleep 5s
#cd /home/juan-rpa/Documents/RPAServerTest
#./sysmonitor.sh
#echo "Starting Health Checker script."


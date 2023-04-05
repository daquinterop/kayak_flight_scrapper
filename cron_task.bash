#!/bin/bash

Game=$(powershell.exe Get-Process | grep -c VNGame)

if [ $Game -lt 1 ]
then
	source /home/diego/Projects/Flight_scrapper/venv/bin/activate
	export PATH=$PATH:/mnt/c/Windows/System32/WindowsPowerShell/v1.0

	python /home/diego/Projects/Flight_scrapper/chicago_bogota.py
	sh -c 'echo 1 >  /proc/sys/vm/drop_caches'
	sh -c 'echo 2 >  /proc/sys/vm/drop_caches'
	sh -c 'echo 3 >  /proc/sys/vm/drop_caches'
fi

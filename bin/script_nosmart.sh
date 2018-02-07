#!/bin/bash

for i in `seq 1 "$@"`;
        do
                echo $i
		python ../../PycharmProjects/TaskScheduler3/standard_scheduler.py /home/cossmic/public_html/Configurator/behaviours/B12 -w 1
        done  

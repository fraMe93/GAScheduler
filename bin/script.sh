#!/bin/bash
export PYTHONPATH=.
for i in `seq 1 "$@"`;
        do
                echo $i
		python ./oldscheduler/smart_scheduler.py ./web/behaviours/B12 -w 1
        done  

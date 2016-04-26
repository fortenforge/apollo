#!/bin/bash

if [ -z "$1" ]; then
    #By default we have two talliers
    NUM_TALLIERS=1
else
    NUM_TALLIERS=$(($1-1))
fi

killall INT python
echo "Starting Aggregate Tallier"
python aggregate_tallier.py > logs/aggregate_tallier.log 2>&1 &
sleep 1
echo "Starting Authority"
python authority.py > logs/authority.log 2>&1 &
for i in $(eval echo {0..$NUM_TALLIERS}); do
    sleep 1
    echo "Starting Tallier $i"
    python tallier.py $i > logs/tallier$i.log 2>&1 &
done
sleep 1
echo "Starting Registrar"
python registrar.py $NUM_TALLIERS > logs/tallier2.log 2>&1 &
sleep 1
echo "Running Main"
python main.py

# Note sleep is selected to make sure all servers are ready to listen on their ports (May need to increase/decrease duration)

#!/bin/bash

if [ -z "$1" ]; then
    #By default we have five talliers
    TALLIER_MAX=4
else
    TALLIER_MAX=$(($1-1))
fi

trap "killall INT python" EXIT
killall INT python > /dev/null 2>&1
echo "Starting Aggregate Tallier"
python aggregate_tallier.py > logs/aggregate_tallier.log 2>&1 &
echo "Starting Authority"
python authority.py > logs/authority.log 2>&1 &
echo "Starting Registrar"
python registrar.py > logs/registrar.log 2>&1 &
sleep 1
for i in $(eval echo {0..$TALLIER_MAX}); do
    echo "Starting Tallier $i"
    # later take an argument for concurrent elections
    python tallier.py $i 3 > logs/tallier$i.log 2>&1 &
done
sleep 1
python demo.py 2>&1

# Note sleep is selected to make sure all servers are ready to listen on their ports (May need to increase/decrease duration)
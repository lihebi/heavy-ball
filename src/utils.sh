#!/bin/bash

check_euid()
{
    if [ $EUID -ne 0 ]
    then
        echo "You need to be root to perform this command."
        exit 1
    fi
}


check_bridge()
{
    return $(brctl show | awk "/^$1[\t\s]+/{exit 1}")
}

wait_for_device()
{
    local device=$1
    local timeout=$2
    local waited=0

    echo -n "waiting for $device..."

    while(! ip link show | grep -q $device); do

        if [ $waited -lt $timeout ]; then
            sleep 1
            waited=$(($waited + 1))
        else
            echo "not found"
            return 1
        fi
    done

    echo "found"
    return 0
}

start_emaneeventservice()
{
    local xml=$1
    local logfile=$2
    local pidfile=$3
    local uuidfile=$4
    local starttime="$5"

    local startoption=""

    if [ -n "$starttime" ]; then
        startoption="--starttime $(date --date "$starttime" "+%H:%M:%S")"
    fi

    if [ -f $xml ]; then

        echo "Starting emaneeventservice: $xml at $starttime"

        emaneeventservice -d "$xml" -l 3 -f "$logfile" \
                          --pidfile "$pidfile" --uuidfile "$uuidfile" \
                          $startoption

        retval=$?
    else

        echo "Missing emaneeventservice XML: $xml"

        retval=1
    fi

    return $retval
}

start_otestpoint_broker()
{
    local xml=$1
    local logfile=$2
    local pidfile=$3
    local uuidfile=$4

    if [ -f $xml ]; then

        echo "Starting otestpoint-broker: $xml"

        otestpoint-broker "$xml" -d -l 3 -f "$logfile" \
                          --pidfile "$pidfile" --uuidfile "$uuidfile"

        retval=$?
    else
        echo "Missing otestpoint-broker XML: $xml"
        retval=1
    fi

    return $retval
}

start_emane()
{
    local xml=$1
    local logfile=$2
    local pidfile=$3
    local uuidfile=$4

    if [ -f $xml ]; then

        echo "Starting emane: $xml"

        emane "$xml" -r -d -l 3 -f "$logfile" \
              --pidfile "$pidfile" --uuidfile "$uuidfile"

        retval=$?
    else
        echo "Missing emane XML: $xml"
        retval=1
    fi

    return $retval
}

start_emaneeventd_and_wait_for_gpspty()
{
    local xml=$1
    local logfile=$2
    local pidfile=$3
    local uuidfile=$4
    local pty=$5

    if [ -f $xml ]; then

        echo "Starting emaneeventd: $xml"

        rm -f "$pty"

        emaneeventd -r -d "$xml" -l 4 -f "$logfile" \
                    --pidfile "$pidfile" --uuidfile "$uuidfile"

        retval=$?

        if [[ $retval == 0 ]]; then

            echo "Waiting for GPS Locatopn PTY: $pty"

            while (! test -f "$pty")
            do
                sleep 1
            done
        fi

    else
        echo "Missing emaneeventd XML: $xml"
        retval=1
    fi

    return $retval
}

start_gpsd()
{
    local pty=$1
    local pidfile=$2

    echo "Starting gpsd: $pty"
    gpsd -P $pidfile -G -n -b `cat $pty`
}

start_otestpoint_recorder()
{
    local xml=$1
    local logfile=$2
    local pidfile=$3
    local uuidfile=$4

    if [ -f $xml ]; then

        echo "Starting otestpoint-recorder: $xml"

        otestpoint-recorder "$xml" -d -l 4 -f "$logfile" \
                            --pidfile "$pidfile" --uuidfile "$uuidfile"

        retval=$?
    else
        echo "Missing otestpoint-recorder XML: $xml"
        retval=1
    fi

    return $retval
}

start_otestpointd()
{
    local xml=$1
    local logfile=$2
    local pidfile=$3
    local uuidfile=$4

    if [ -f $xml ]; then

        echo "Starting otestpointd: $xml"

        otestpointd "$xml" -d -l 4 -f "$logfile" \
                    --pidfile "$pidfile" --uuidfile "$uuidfile"

        retval=$?
    else
        echo "Missing otestpointd XML: $xml"
        retval=1
    fi

    return $retval
}

start_routing()
{
    local routingconf=$1
    olsrd -f "$routingconf"
}

start_mgen()
{
    local mgeninput=$1
    local mgenoutput=$2
    local pidfile=$3
    local logfile=$4
    local starttime="$5"

    local startoption=""

    if [ -n "$starttime" ]; then
        startoption="start $(date --date "$starttime" "+%H:%M:%S" --utc)GMT"
        echo "Starting mgen: input $mgeninput output $mgenoutput $startoption"
    else
        echo "Starting mgen: input $mgeninput output $mgenoutput now"
    fi

    # calling mgen with input config. No node id is passed. The
    # mgeninput is mgen config in the demo folder. (HEBI: mgen is used
    # in  1, 3, 5, 8)
    nohup mgen             \
          input $mgeninput   \
          output $mgenoutput \
          $startoption       \
          txlog &> $logfile &

    echo $! > $pidfile
}

start_mgen_mod()
{
    echo "Starting mgen mod .."
    local mgeninput=$1
    local mgenoutput=$2
    local pidfile=$3
    local logfile=$4
    local starttime="$5"
    local nodeId="$6" 
    local nodecount="$7"

    local startoption=""

    if [ -n "$starttime" ]; then
        startoption="$(date --date "$starttime" "+%H:%M:%S" --utc)GMT"
        echo "Starting mgen: input $mgeninput output $mgenoutput $startoption"
    else
        # FIXME if startoption is "", python won't receive any input,
        # the fifo.py script parsing arg will be buggy.
        #
        # This is not used in the new fifo.py script. It uses the
        # current time + 10sec as startup time
        echo "Starting mgen: input $mgeninput output $mgenoutput now"
    fi

    echo "really starting .."

    # custom mgen
    # FIXME why nohup?
    # FIXME why -u
    nohup python -u $mgeninput    \
          $startoption $nodeId $nodecount \
        &> $logfile &

    echo $! > $pidfile
    echo "Done"
}

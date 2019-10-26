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

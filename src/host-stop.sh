#!/bin/bash

bridge=emanenode0
nodecount=4

source utils.sh

function collect_statistics {
    for nodeid in $(seq 1 $nodecount)
    do
        name=node-$nodeid
        echo "Collecting statistics and configuration from $name"
        echo "HEBI: Skipped."
        # emanesh $name show >  persist/$nodeid/var/log/emane.show
        # emanesh $name get stat '*' all >  persist/$nodeid/var/log/emane.stats
        # emanesh $name get table '*' all >  persist/$nodeid/var/log/emane.tables
        # emanesh $name get config '*' all >  persist/$nodeid/var/log/emane.config
    done
}

function stop_lxc {
    for nodeid in $(seq 1 $nodecount)
    do
        echo "Stopping lxc instance: node-$nodeid"
        # actually it looks like I don't need to perform extra cleaning
        # for the pids running inside VMs.
        lxc-stop -n node-$nodeid -k
    done
}

function magic_clean_1 {
    # kill processes and remove pid files

    if [ -f host-tmp/otestpoint-broker.pid ]
    then
        kill -QUIT $(cat host-tmp/otestpoint-broker.pid)
        rm -f host-tmp/otestpoint-broker.pid
    fi

    if [ -f host-tmp/emaneeventservice.pid ]
    then
        kill -QUIT $(cat host-tmp/emaneeventservice.pid)
        rm -f host-tmp/emaneeventservice.pid
    fi
}

function remove_bridge {
    # remove bridge
    if (! check_bridge $bridge)
    then
        echo "Removing bridge: $bridge"

        ip link set $bridge down

        brctl delbr $bridge

        iptables -D INPUT -i $bridge -j ACCEPT

        iptables -D FORWARD -i $bridge -j ACCEPT
    fi
}

function magic_clean_2 {

    # This is performed
    for vif in $(ip link show | awk -F : '/veth[0-9]+\.[0-9]/{gsub(/@if[0-9]+/,"",$2); print $2;}')
    do
        echo "Performing extra cleanup of vif $vif"
        ip link del dev $vif 2>&1 > /dev/null
    done

    # paranoia - make sure everything is down
    for i in $(ps ax | awk '/emaneeventservic[e] /{print $1}')
    do
        echo "Performing extra cleanup of emaneeventservice [$i]"
        kill -9 $i;
    done

    for i in $(ps ax | awk '/emanetransport[d] /{print $1}')
    do
        echo "Performing extra cleanup of emanetransportd [$i]"
        kill -9 $i;
    done

    for i in $(ps ax | awk '/eman[e] /{print $1}')
    do
        echo "Performing extra cleanup of emane [$i]"
        kill -9 $i;
    done

}

function main {
    check_euid
    collect_statistics
    stop_lxc
    echo "Magic clean 1"
    magic_clean_1
    remove_bridge
    echo "Magic clean 2"
    magic_clean_2
}

main

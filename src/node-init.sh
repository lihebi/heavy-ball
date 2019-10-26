#!/bin/bash

cd $1

nodeid=$2
nodecount=$3

start_sshd()
{
    # I believe this pid file is used for kill the process
    local pidfile=$1
    /usr/sbin/sshd -o "PidFile=$pidfile"
}

source utils.sh

# fix devpts
mount /dev/pts -o remount,rw,mode=620,ptmxmode=666,gid=5

# FIXME remove old
mkdir -p $PWD/tmp
start_sshd $PWD/tmp/ssh.$nodeId.pid

echo "starting emane .."
start_emane \
    xml/platform$nodeId.xml \
    $PWD/tmp/emane.$nodeId.log \
    $PWD/tmp/emane.$nodeId.pid \
    $PWD/tmp/emane.$nodeId.uuid

echo "starting emaneeventd .."
start_emaneeventd_and_wait_for_gpspty \
    xml/eventdaemon$nodeId.xml \
    $PWD/tmp/emaneeventd.$nodeId.log  \
    $PWD/tmp/emaneeventd.$nodeId.pid  \
    $PWD/tmp/emaneeventd.$nodeId.uuid \
    $PWD/tmp/gps.$nodeId.pty

start_gpsd \
    $PWD/tmp/gps.$nodeId.pty \
    $PWD/tmp/gpsd.$nodeId.pid

start_otestpoint_recorder \
    xml/otestpoint-recorder$nodeId.xml \
    $PWD/tmp/otestpoint-recorder.$nodeId.log \
    $PWD/tmp/otestpoint-recorder.$nodeId.pid \
    $PWD/tmp/otestpoint-recorder.$nodeId.uuid

start_otestpointd \
    xml/otestpointd$nodeId.xml \
    $PWD/tmp/otestpointd.$nodeId.log \
    $PWD/tmp/otestpointd.$nodeId.pid \
    $PWD/tmp/otestpointd.$nodeId.uuid

# olsrd -f "$routingconf"
start_routing routing$nodeId.conf

# TODO enable this
# start_mgen_mod \
#     mgen_fifo$nodeId.py \
#     $PWD/tmp/mgen.$nodeId.out \
#     $PWD/tmp/mgen.$nodeId.pid \
#     $PWD/tmp/mgen.$nodeId.log \
#     "$starttime" \
#     "$nodeId" "$nodecount"

# starting mgen on clients? with the same mgen config
start_mgen \
    mgen \
    $PWD/tmp/mgen.$nodeId.out \
    $PWD/tmp/mgen.$nodeId.pid \
    $PWD/tmp/mgen.$nodeId.log \
    "$starttime"

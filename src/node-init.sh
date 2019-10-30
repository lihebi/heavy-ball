#!/bin/bash

export PATH=$PATH:/sbin:/usr/sbin:/usr/local/bin:/usr/local/sbin

cd $1
echo `pwd`

nodeid=$2
nodecount=$3

echo "node  $nodeid init"

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
start_sshd $PWD/tmp/ssh.$nodeid.pid
# chown -R $SUDO_USER:`id -gn $SUDO_USER` host-tmp

start_emane \
    xml/platform$nodeid.xml \
    $PWD/tmp/emane.$nodeid.log \
    $PWD/tmp/emane.$nodeid.pid \
    $PWD/tmp/emane.$nodeid.uuid

# This requires gpsdlocationagent1.xml
start_emaneeventd_and_wait_for_gpspty \
    xml/eventdaemon$nodeid.xml \
    $PWD/tmp/emaneeventd.$nodeid.log  \
    $PWD/tmp/emaneeventd.$nodeid.pid  \
    $PWD/tmp/emaneeventd.$nodeid.uuid \
    $PWD/tmp/gps.$nodeid.pty

start_gpsd \
    $PWD/tmp/gps.$nodeid.pty \
    $PWD/tmp/gpsd.$nodeid.pid

start_otestpoint_recorder \
    xml/otestpoint-recorder$nodeid.xml \
    $PWD/tmp/otestpoint-recorder.$nodeid.log \
    $PWD/tmp/otestpoint-recorder.$nodeid.pid \
    $PWD/tmp/otestpoint-recorder.$nodeid.uuid

start_otestpointd \
    xml/otestpointd$nodeid.xml \
    $PWD/tmp/otestpointd.$nodeid.log \
    $PWD/tmp/otestpointd.$nodeid.pid \
    $PWD/tmp/otestpointd.$nodeid.uuid

start_routing xml/routing$nodeid.conf

echo "starting mgen .."

start_mgen_mod \
    mgen_fifo$nodeid.py \
    $PWD/tmp/mgen.$nodeid.out \
    $PWD/tmp/mgen.$nodeid.pid \
    $PWD/tmp/mgen.$nodeid.log

echo "End of node-init"

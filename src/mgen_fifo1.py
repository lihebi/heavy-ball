#!/usr/bin/env python2

import os
import mgen
import math
import datetime
import socket
import time
import sys
import threading
import stat
import datetime
from Queue import Queue

PKT_SIZE = 512

A_MAX = 100.0
EPSILON = 0.50
K_PARA = 200.0

def test_fifo():
    os.mkfifo('test_fifo.sock')
    with open('test_fifo.sock', 'r') as f:
        print f.readline()
    with open('/tmp/emane-mgen_fifo_node1', 'w') as f:
        f.write('hello\n')

def send_init_rate(sender, rates):
    """Send rates events.

    rates should be a map from id to rate.
    """
    for ID, rate in rates.iteritems():
        s = "1.0 ON {} UDP SRC 5001 DST 10.100.0.{}/5001 PERIODIC [{} {}] INTERFACE bmf0".format(
            ID, ID, rate, PKT_SIZE)
        sender.send_event(s)

def send_mod_rate(sender, rates):
    """Send mod rate events."""
    for ID, rate in rates.iteritems():
        s = "0.0 MOD {} UDP SRC 5001 DST 10.100.0.{}/5001 PERIODIC [{} {}] INTERFACE bmf0".format(ID, ID, rate, PKT_SIZE)
        sender.send_event(s)

def get_init_rate(nodeid, numnodes):
    INIT_FLOW = 5
    res = {}
    for i in range(1, numnodes+1):
        if i != nodeid:
            res[i] = INIT_FLOW
    return res

def process_data(data, oldrates):
    """compute and return new rates"""
    totalrate = 0
    totalql = 0
    rates = oldrates.copy()
    for weight in data.split(','):
        wid = int(weight.split(':')[0])
        w = float(weight.split(':')[1])
        ql = float(weight.split(':')[2])
        totalql += ql
        if w == 0:
            rate = int(A_MAX)
        else:
            rate = int(K_PARA/w - EPSILON)
        if rate < 0:
            rate = 0
        elif rate > A_MAX:
            rate = int(A_MAX)

        totalrate += rate
        if rate != rates[wid]:
            rates[wid] = rate
    return rates, totalrate, totalql

def read_emane_fifo():
    """This will block."""
    nodeid=1
    path = "/tmp/emane-mgen_fifo_node{}".format(nodeid)
    if not os.path.exists(path):
        os.mkfifo(path)
        # /tmp folder has the sticky bit, other users cannot write
        os.chmod(path, 0o777)
    with open(path, 'r') as fifo:
        data = fifo.readline()[:-1]
        return data.replace('\x00', '')

g_q = Queue()
def mgen_flow(starttime, nodeid, numnodes):
    """generate mgen control flow.

    """
    sender = mgen.Controller()
    sender.send_command("output tmp/mgen.{}.out".format(nodeid))
    sender.send_command("start " + starttime)
    sender.send_command("txlog")
    print("start mgen")

    rates = get_init_rate(nodeid, numnodes)
    send_init_rate(sender, rates)

    global g_q
    # A separate thread for consuming the queue and sending to plot
    t = threading.Thread(target=queue_worker)
    t.daemon = True
    t.start()

    init_t = -1
    while True:
        data = read_emane_fifo()
        if init_t is -1:
            # The first read from emane, the mgen start
            init_t = time.time()
        print datetime.datetime.now(), "Reader: ", data
        newrates, rate, ql = process_data(data, rates)
        rates = newrates
        # I actually should spin a thread rather than not blocking
        # here. Otherwise, emane might very well stopped because
        # nobody is reading the pipe. Also, the time here would be
        # inaccurate.
        #
        # send_to_plot(time.time() - init_t, rate, ql)
        g_q.put((time.time() - init_t, rate, ql))

def queue_worker():
    global g_q
    while True:
        dt, totalrate, totalql = g_q.get()
        send_to_plot(dt, totalrate, totalql)
        g_q.task_done()

def send_to_plot(dt, totalrate, totalql):
    plot_path = "/tmp/plot_fifo"
    # FIXME maybe I should just open it once? It worked fine now.
    with open(plot_path, 'w') as fifo:
        s = "{}:{}:{},".format(dt, totalrate, totalql)
        print 'Sending', s, ' ..'
        fifo.write(s)

def main():
    # looks like I have to give a time. How about now+1sec
    t = datetime.datetime.utcnow()
    dt = datetime.timedelta(seconds=10)
    t = t + dt
    tstr = t.strftime("%H:%M:%SGMT")

    print "Using now+5sec for startint time, that is, {}".format(tstr)

    starttime = tstr
    nodeid = 1
    numnodes = 4

    print 'Starting flow ..'
    # start_flow(starttime, nodeid, numnodes)
    mgen_flow(starttime, nodeid, numnodes)
    print 'Finished'

if __name__ == "__main__":
    main()

import os
import mgen
import math
import datetime
import socket
import time
import sys
import threading
import stat

PKT_SIZE = 512
INIT_FLOW = 5

# i = 1
A_MAX = 100.0
EPSILON = 0.50
K_PARA = 200.0

plot_path = "/tmp/plot_fifo"

def main():
    starttime = sys.argv[1]
    nodeid = int(sys.argv[2])
    numnodes = int(sys.argv[3])

    t1 = threading.Thread(target=start_flow, args=(starttime,nodeid,numnodes,)) 
    t2 = threading.Thread(target=switch_control) 
  
    # starting thread 1 
    t1.start() 
    # starting thread 2 
    t2.start() 

    t1.join()
    t2.join()


def switch_control():
    global switch
    switch = False
    switch_file = "/tmp/mgen_switch"
    # plot_path = "/tmp/plot_fifo"
    if os.path.exists(switch_file):
        os.remove(switch_file)
    os.mkfifo(switch_file)
    os.chmod(switch_file, stat.S_IWOTH)

    while True:
        with open(switch_file, 'r') as fifo:
            line = fifo.read()
            if line == 'on':
                switch = True
                print "switch on"
            elif line == 'off':
                switch = False
                print "switch off"
                if os.path.exists(plot_path):
                    os.remove(plot_path)
            else: 
                # switch = False
                print "Switch: ", line

def start_flow(starttime,nodeid,numnodes):

    curr_rates = {}
    for i in range(1, numnodes+1):
        if i != nodeid:
            curr_rates[i] = INIT_FLOW

    sender = mgen.Controller()
    sender.send_command("output persist/{}/var/log/mgen.out".format(nodeid))
    sender.send_command("start " + starttime)
    sender.send_command("txlog")
    print("start mgen")

    # "Manually"  start a flow from this sender
    # sender.send_event("on 1 udp dst 127.0.0.1/5000 per [1 1024]")

    for ind, rate in curr_rates.iteritems():
        onevent = "1.0 ON {} UDP SRC 5001 DST 10.100.0.{}/5001 PERIODIC [{} {}] INTERFACE bmf0".format(
            ind, ind, rate, PKT_SIZE)
        print(onevent)
        sender.send_event(onevent)

    print(datetime.datetime.now())

    start = int(round(time.time() * 1000))


    fifo_path = "/tmp/emane-mgen_fifo_node{}".format(nodeid)
    if os.path.exists(fifo_path):
        os.remove(fifo_path)
    os.mkfifo(fifo_path)

    # plot_path = "/tmp/plot_fifo"
    # if os.path.exists(plot_path):
    #     os.remove(plot_path)
    # os.mkfifo(plot_path)


    # a forever loop until we interrupt it or
    # an error occurs
    totalrate = 0
    totalql = 0
    startTx = 0
    lastrate = 300
    lastql = 0


    hasStart = True
    while True:
        # Establish connection with client.
        with open(fifo_path, 'r') as fifo:
            data = fifo.readline()[:-1]
            print datetime.datetime.now(), "Reader: ", data

        # if now - start < 50 * 1000:
        #     continue
        if not switch:
            print('waiting')
            if hasStart:
                print("reset mgen")
                for wid in curr_rates.iterkeys():
                    mod_event = "MOD {} UDP SRC 5001 DST 10.100.0.{}/5001 PERIODIC [{} {}] INTERFACE bmf0".format(wid, wid, INIT_FLOW, PKT_SIZE)
                    curr_rates[wid] = INIT_FLOW
                    sender.send_event(mod_event)
                # if os.path.exists(plot_path):
                #     os.remove(plot_path)
                # os.mkfifo(plot_path)
            # time.sleep(0.01)
            hasStart = False
            continue

        now = int(round(time.time() * 1000))
        # i = i+1
        # if 50 < i:
        totalrate = 0
        totalql = 0
        
        if len(data.split(',')) > 3:
            continue

        for weight in data.split(','):
            wid = int(weight.split(':')[0])
            w = float(weight.split(':')[1])
            ql = float(weight.split(':')[2])
            totalql += ql
            # print "wid", wid
            # print "w", w
            if w == 0:
                rate = int(A_MAX)
            else:
                rate = int(K_PARA/w - EPSILON)
            if rate < 0:
                rate = 0
            elif rate > A_MAX:
                rate = int(A_MAX)

            totalrate += rate
            mod_event = "MOD {} UDP SRC 5001 DST 10.100.0.{}/5001 PERIODIC [{} {}] INTERFACE bmf0".format(wid, wid, rate, PKT_SIZE)
            print datetime.datetime.now(), mod_event
            print datetime.datetime.now(), data

            if rate != curr_rates[wid]:
                curr_rates[wid] = rate
                sender.send_event(mod_event)

        if lastrate != 300 and totalrate != 300 and lastrate > 5:
            if not hasStart:
                hasStart = True
                print("reset start time")
                startTx = now
            t1 = threading.Thread(target=send_to_plot, args=(now, startTx, lastrate, lastql,)) 
            # starting thread 1 
            t1.start() 
        lastrate = totalrate
        lastql = totalql

def send_to_plot(now, startTx, totalrate, totalql):
    print 'before open'
    try:
        with open(plot_path, 'w') as fifo:
            print "before write"
            fifo.write("{}:{}:{},".format((now - startTx)/1000.0, totalrate, totalql))
            print "after wirte"
    except:
        print 'file removed'

if __name__ == "__main__":
    main()
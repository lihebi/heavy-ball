#!/usr/bin/env python3

import subprocess
import threading
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy as np
import time
import stat
from matplotlib.animation import FuncAnimation

# this is the plot client


""" Create /tmp/schedule-1hop-<beta>.xml and return the filename.

"""
def create_schedule(beta=0.2):
    label = "BETA_{:.2f}".format(beta)
    # tmpFolder = os.path.join('/tmp/', self.mainTmpFolder, label)
    # self.allData.append(tmpFolder)
    # os.mkdir(tmpFolder)

    schedule = '<emane-tdma-schedule >\n\
    <structure frames="1" slots="2" slotoverhead="0" slotduration="1500" bandwidth="1M" beta="{}"/>\n\
    <multiframe frequency="2.4G" power="0" class="0" datarate="1M">\n\
        <frame index="0">\n\
            <slot index="0" nodes="1"/>\n\
            <slot index="1" nodes="2:4"/>\n\
        </frame>\n\
    </multiframe>\n\
</emane-tdma-schedule>'.format(beta)
    tmpFile = os.path.join('/tmp/', 'schedule-1hop-{}.xml'.format(beta))
    with open(tmpFile, "w") as f:
        f.writelines(schedule)
    print(schedule)
    # return(tmpFolder, tmpFile)
    return tmpFile

def read_plot_fifo():
    """Read plot data and return. This will block."""
    fname = '/tmp/plot_fifo'
    if not os.path.exists(fname):
        os.mkfifo(fname)
        # add other write permission
        os.chmod(fname, 0o777)
    with open(fname, "r") as fifo:
        print('fifo opened')
        return fifo.read()

g_x = []
g_y1 = []
g_y2 = []
def fifo_receiver():
    """Keep reading fifo and pop in new data to a global variable."""
    global g_x
    global g_y1
    global g_y2
    while True:
        # this is blocking
        data = read_plot_fifo()
        data = list(filter(lambda s: s, data.split(',')))
        print('Read: "{}"'.format(data))
        y1s = []
        y2s = []
        xs = []
        for one in data:
            if one != "":
                y1s.append(float(one.split(':')[1]))
                y2s.append(float(one.split(':')[2]))
                xs.append(float(one.split(':')[0]))

        g_y1 = np.append(g_y1[:], y1s[:])
        g_y2 = np.append(g_y2[:], y2s[:])
        g_x = np.append(g_x[:], xs[:])
    
def animated_plot():
    # plt.ion()
    global g_x
    global g_y1
    global g_y2
    fig = plt.figure(figsize=(13, 13))
    ax1 = fig.add_subplot(211)
    # FIXME plt.? apply to ax1?
    plt.ylabel('Source Rate')
    plt.title('Source Rate vs Time(s)')
    plt.xlabel('Time(s)')
    ax2 = fig.add_subplot(212)
    # update plot label/title
    plt.ylabel('Queue Length')
    plt.title('Queue Length vs Time(s)')
    plt.xlabel('Time(s)')
    # plt.show()
    lastlen = 0
    def update(i):
        nonlocal lastlen
        if lastlen != len(g_x):
            lastlen = len(g_x)
            print('len of x:', len(g_x))
            ax1.plot(g_x, g_y1)
            ax2.plot(g_x, g_y2)
    ani = FuncAnimation(fig, update)
    # FIXME reopen if closed
    # FIXME why colors changing all the time?
    plt.show()


# 1. send schedule
# 2. set /tmp/mgen-switch
# 3. receive data and plot

def main():
    """This should be just waiting on plot data."""

    # print('starting emane ..')
    # subprocess.run(['./host-start.sh'])

    # FIXME this is actually 0.5
    # print('sending default schedule ..')
    # subprocess.run(['emaneevent-tdmaschedule',
    #                 '/home/hebi/git/heavy-ball/src/xml/schedule-1hop.xml',
    #                 '-i', 'emanenode0'])

    # print('creating schedule ..')
    # fname = create_schedule(0.2)
    # print('sending plot schedule ..')
    # subprocess.run(['emaneevent-tdmaschedule', fname, '-i', 'emanenode0'])
    # print("schedule sent.")

    # OK, I need a thread to read fifo data, and store it in a global
    # variable
    t1 = threading.Thread(target=fifo_receiver) 
    t1.start()

    # Then, the plot simply read that variable
    animated_plot()

if __name__ == '__main__':
    main()

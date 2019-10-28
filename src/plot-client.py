#!/usr/bin/env python3

import subprocess
import threading
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import time
import stat
from matplotlib.animation import FuncAnimation

def create_schedule(beta=0.2):
    """Create /tmp/schedule-1hop-<beta>.xml and return the filename.

    """
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

g_x = []
g_y1 = []
g_y2 = []
def fifo_receiver():
    """Keep reading fifo and pop in new data to a global variable."""
    global g_x
    global g_y1
    global g_y2
    # just open the pipe once
    fname = '/tmp/plot_fifo'
    if not os.path.exists(fname):
        os.mkfifo(fname)
        # add other write permission
        os.chmod(fname, 0o777)
    with open(fname, "r") as fifo:
        while True:
            data = fifo.read()
            data = list(filter(lambda s: s, data.split(',')))
            if data:
                # print('Got: {}'.format(data))
                y1s = []
                y2s = []
                xs = []
                for one in data:
                    y1 = float(one.split(':')[1])
                    y2 = float(one.split(':')[2])
                    x = float(one.split(':')[0])
                    if x == 0:
                        print('Received stop message. Returning.')
                        return
                    y1s.append(y1)
                    y2s.append(y2)
                    xs.append(x)
                g_y1 = np.append(g_y1[:], y1s[:])
                g_y2 = np.append(g_y2[:], y2s[:])
                g_x = np.append(g_x[:], xs[:])
            else:
                # FIXME do I need to sleep here to save CPU?
                time.sleep(0.1)

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
            if len(g_x) != len(g_y1) or len(g_x) != len(g_y2):
                # It looks like there might be inconsistent update for
                # x and y. This should be the receiver inconsistency,
                # and should recover itself.
                print('WARNING: dimension does not match: ',
                      len(g_x), len(g_y1), len(g_y2))
                l = min(len(g_x), len(g_y1), len(g_y2))
                ax1.plot(g_x[:l], g_y1[:l])
                ax2.plot(g_x[:l], g_y2[:l])
            else:
                # FIXME still have unmatched dimension error
                ax1.plot(g_x, g_y1)
                ax2.plot(g_x, g_y2)
    ani = FuncAnimation(fig, update, interval=1000)
    # TODO reopen if closed
    plt.show()

def simple_plot(x, y1, y2, fname):
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
    ax1.plot(g_x, g_y1)
    ax2.plot(g_x, g_y2)
    plt.savefig(fname)
    plt.close()

# 1. send schedule
# 2. set /tmp/mgen-switch
# 3. receive data and plot

def exp():
    # TODO put starting emane and changing beta elsewhere
    exp_beta(0.0)
    exp_beta(0.1)
    exp_beta(0.3)
    exp_beta(0.5)
    exp_beta(0.7)
    exp_beta(0.9)

def exp_beta(beta):
    # test whether
    if os.path.exists('data/beta-{}.pdf'.format(beta)):
        print('already tested {}'.format(beta))
        return
    print('starting emane ..')
    subprocess.run(['sudo', './host-start.sh'])

    time.sleep(0.5)
    print('sleeping 10 seconds for mgen fifo ..')
    time.sleep(10)
    
    print('creating schedule ..')
    fname = create_schedule(beta)
    print('sending plot schedule ..')
    subprocess.run(['emaneevent-tdmaschedule', fname, '-i', 'emanenode0'])
    print("schedule sent.")
    
    # TODO also need to reset fifo.py. How to communicate with fifo.py?
    #
    # This involve complicated message sending between nodes and
    # host. Not using it.

    # save data and plot
    print('starting fifo_receiver ..')
    t1 = threading.Thread(target=fifo_receiver)
    t1.start()
    t1.join()

    # TODO save the data for combined plot
    print('saving plot ..')
    if not os.path.exists('data'):
        os.makedirs('data')

    global g_x, g_y1, g_y2
    simple_plot(g_x, g_y1, g_y2, 'data/beta-{}.pdf'.format(beta))

    # save data
    print('saving data ..')
    np.save('data/beta-{}-x.dat'.format(beta), g_x)
    np.save('data/beta-{}-y1.dat'.format(beta), g_y1)
    np.save('data/beta-{}-y2.dat'.format(beta), g_y2)

    # clean up data for next experiment
    g_x = []
    g_y1 = []
    g_y2 = []

    # clean up
    print('stopping the network ..')
    subprocess.run(['sudo', './host-stop.sh'])

def plot_all():
    # - loop through all data/
    # - infer beta from filename
    # - plot everything in a single frame
    #
    # TODO verify shape
    d = 'data'
    fnames = os.listdir(d)
    def func(s):
        m = re.search('beta-(.*)-x.dat.npy', s)
        if m:
            return m.group(1)
    betas = list(sorted(map(float, filter(lambda x: x, map(func, fnames)))))
    if betas:
        print('For betas: {}'.format(betas))
        fig = plt.figure(figsize=(13, 13))
        ax1 = fig.add_subplot(211)
        plt.ylabel('Source Rate')
        plt.title('Source Rate vs Time(s)')
        plt.xlabel('Time(s)')
        ax2 = fig.add_subplot(212)
        plt.ylabel('Queue Length')
        plt.title('Queue Length vs Time(s)')
        plt.xlabel('Time(s)')
        lastlen = 0
        colors  = ['r','g','b','c', 'm', 'y']
        for beta, color in zip(betas, colors*3):
            x = np.load(os.path.join(d, 'beta-{}-x.dat.npy'.format(beta)))
            y1 = np.load(os.path.join(d, 'beta-{}-y1.dat.npy'.format(beta)))
            y2 = np.load(os.path.join(d, 'beta-{}-y2.dat.npy'.format(beta)))
            # different color
            ax1.plot(x, y1, color=color, label='beta={}'.format(beta))
            ax2.plot(x, y2, color=color, label='beta={}'.format(beta))
        ax1.legend()
        ax2.legend()
        plt.savefig('data/all.pdf')
        plt.close()
        
def main():
    """This should be just waiting on plot data."""
    # A thread to read fifo data, and store it in a global variable
    t1 = threading.Thread(target=fifo_receiver)
    t1.start()

    # Then, the plot simply read that variable
    animated_plot()

if __name__ == '__main__':
    # main()
    exp()
    plot_all()

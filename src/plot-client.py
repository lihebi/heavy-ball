#!/usr/bin/env python3

import subprocess
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy as np
import time
import stat

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

def test_fifo():
    fifo_path = "/tmp/plot_fifo"
    with open(fifo_path, "r") as fifo:
        print("FIFO opened")

def read_plot_fifo():
    """Read plot data and return. This will block."""
    fname = '/tmp/plot_fifo'
    if not os.path.exists(fifo_path):
        os.mkfifo(fifo_path)
        # add other write permission
        os.chmod(fifo_path, 0o777)
    with open(fifo_path, "r") as fifo:
        print('fifo opened')
        data = fifo.read().split(',')
        return data

def newplot():
    """How should I (live) plot?

    First, why live plot? Mostly for performance reason.

    OK, I'll do live plot.

    """
    x_vec = []
    y1_vec = []
    y2_vec = []
    line1 = []
    line2 = []
    while True:
        data = read_plot_fifo()
        print('Read: "{}"'.format(data))
        # FIXME this should not happen anymore
        if len(data) == 1 and data[0] == '':
            print('Receiving empty data, breaking ..')
            continue
        y1s = []
        y2s = []
        xs = []
        for one in data:
            if one != "":
                y1s.append(float(one.split(':')[1]))
                y2s.append(float(one.split(':')[2]))
                xs.append(float(one.split(':')[0]))

        y1_vec = np.append(y1_vec[:], y1s[:])
        y2_vec = np.append(y2_vec[:], y2s[:])
        x_vec = np.append(x_vec[:], xs[:])
        line1, line2 = live_plotter(x_vec, y1_vec, y2_vec, line1, line2)

def live_plotter(x_vec, y1_data, y2_data, line1, line2, identifier='',
                 pause_time=0.001):
    if line1 == []:
        # this is the call to matplotlib that allows dynamic plotting
        print('line1')
        plt.ion()
        fig = plt.figure(figsize=(13, 13))
        ax1 = fig.add_subplot(211)
        # create a variable for the line so we can later update it
        line1, = ax1.plot(x_vec, y1_data, alpha=0.6)
        # update plot label/title
        plt.ylabel('Source Rate')
        plt.title('Source Rate vs Time(s)')
        plt.xlabel('Time(s)')
        plt.xlim([0, 6.0])
        plt.ylim([0, 350])

        ax1 = fig.add_subplot(212)
        # create a variable for the line so we can later update it
        line2, = ax1.plot(x_vec, y2_data, alpha=0.6)
        # update plot label/title
        plt.ylabel('Queue Length')
        plt.title('Queue Length vs Time(s)')
        plt.xlabel('Time(s)')
        plt.xlim([0, 6.0])
        plt.ylim([0, 40])

        plt.show()

    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    line1.set_xdata(x_vec)

    line2.set_ydata(y2_data)
    line2.set_xdata(x_vec)
    # adjust limits if new data goes beyond bounds
    plt.subplot(211)
    plt.pause(pause_time)

    plt.subplot(212)
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return (line1, line2)


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

    print('starting live plotting ..')
    newplot()

if __name__ == '__main__':
    main()

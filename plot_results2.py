from util.helper import *
from collections import defaultdict
from math import sqrt
import numpy as np
import argparse
import re
import os

from matplotlib import cm

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--baseline', dest='baseline_cwnd',
                    type=int,
                    help="Specify the cwnd size that should be\
 considered the baseline") 
parser.add_argument('-f', dest="path", required=True)
parser.add_argument('-p', dest="show_pct", type=bool, default=False)
parser.add_argument('-o', '--out', dest="out", default=None)

args = parser.parse_args()

def parse_filename(name):
    regex_filename = 'cwnd-(\d+)-rtt-(\d+).txt'
    match = re.match(regex_filename, name)
    if match is None:
        return None
    else:
        return int(match.group(1)), int(match.group(2))

def parse_file(f):
    regex_num = '\d+\.\d*'
    pattern_num = re.compile(regex_num)
    minimum = maximum = avg = std = median = 0
    with open(f) as opened:
        n = 1
        avg = 0.0
        for l in opened:
            parts = l.split(":")
            if len(parts) == 2:
                nums = pattern_num.findall(parts[1])
                if parts[0] == 'cwnd':
                    cwnd = int(parts[1])
                elif parts[0] == 'rtt':
                    rtt = int(parts[1])
                elif parts[0] == 'bandwidth':
                    bandwidth = int(parts[1])
                elif parts[0] == 'bdp':
                    bdp = int(parts[1])
            elif len(parts) == 1:
                nums = pattern_num.findall(parts[0])
                if len(nums) == 0:
                    continue
                num = float(nums[0])
                avg = ((n-1)*avg + num)/n
                n = n + 1
            else:
                assert 0, "2 or more colons in line: Danger!"

    return avg*1000, cwnd, rtt, bandwidth, bdp

def generate_data_dict():
    data = dict() # maps from rtts to cwnds to latency
    for infile in os.listdir(args.path):
        params = parse_filename(infile)
        if params is None:
            continue

        cwnd, rtt = params
        avg, cwnd, rtt2, bwidth, bdp = parse_file(args.path + infile)
        assert rtt == rtt2
        
        if rtt not in data:
            data[rtt] = dict()
        data[rtt][cwnd] = avg

    return data

def get_num_cwnds(data):
    return len(data[data.keys()[0]].keys())

def get_num_rtts(data):
    return len(data.keys())

def plot_improvement(data, ax_abs, ax_percent):
    width = 0.25
    labels = list()
    # These two are used only for baseline mode
    abs_list = list()
    percent_list = list()
    # Used only for non-baseline mode
    abs_vals = dict()
    
    rtts = data.keys()
    num_cwnds = get_num_cwnds(data)
    if args.baseline_cwnd:
        assert 2 == num_cwnds, "Baseline mode only supports\
 comparing two congestion windows"
    for rtt in sorted(rtts):
        labels.append('%d' % rtt)
        cwnds = data[rtt]
        assert num_cwnds == len(cwnds.keys())
        for cwnd in sorted(cwnds.keys()):
            if args.baseline_cwnd and cwnd != args.baseline_cwnd:
                avg = data[rtt][cwnd]
                b_avg = data[rtt][args.baseline_cwnd]
                diff = b_avg - avg
                pcnt = diff / avg

                print rtt, cwnd, "  Results:", diff, pcnt

                abs_list.append(diff)
                percent_list.append(pcnt)
            else:
                if cwnd not in abs_vals:
                    abs_vals[cwnd] = list()
                abs_vals[cwnd].append(data[rtt][cwnd])
        
    ind = np.arange(len(rtts))
    if args.baseline_cwnd:
        rects1 = ax_abs.bar(ind+width, abs_list, width, color='r')
        if ax_percent is not None:
            rects2 = ax_percent.bar(ind+2*width, percent_list, width, color='b')
            ax_abs.legend( (rects1[0], rects2[0]),
                           ('Absolute Improvement','Percentage Improvement'),
                           loc=2)
        else:
            ax_abs.legend( [rects1[0]],
                           ['Absolute Improvement'],
                           loc=2)
    else:
        rectZeros = list()
        legendLabels = list()
        per_bar_width = width * 2 / num_cwnds
        i = 0
        for key in sorted(abs_vals.keys()):
            rects1 = ax_abs.bar(ind+(i+num_cwnds/2)*per_bar_width,
                                abs_vals[key], per_bar_width,
                                color=cm.jet(1.*i/num_cwnds))
            rectZeros.append(rects1[0])
            legendLabels.append('Total Latency for cwnd %d' % key)
            i = i + 1

        l = ax_abs.legend( tuple(rectZeros), tuple(legendLabels), loc=2 )
        #l.set_zorder(0)

    ax_abs.set_xticks(ind+2*width)
    ax_abs.set_xticklabels( tuple(labels) )

# Begin script
m.rc('figure', figsize=(16, 6))
fig = plt.figure()

ax1 = fig.add_subplot(1, 1, 1)

ax1.set_xlabel("RTT (msec)")
if args.baseline_cwnd:
    ax1.set_ylabel("Improvement (ms)", color="r")
else:
    ax1.set_ylabel("Absolute Latency (ms)", color="r")
ax1.set_yscale("log")
ax1.grid(True, which='major', linestyle='-')
ax1.set_axisbelow(True)
if args.baseline_cwnd:
    ax1.set_ylim(1, 10000)
else:
    ax1.set_ylim(50, 5000)

#http://matplotlib.sourceforge.net/examples/api/two_scales.html#api-two-scales
ax2 = None    
if args.baseline_cwnd and args.show_pct:
    ax2 = ax1.twinx()
    ax2.set_ylabel("Percentage Improvement",color="b")
    ax2.set_yscale("linear")
    ax2.set_ylim(0, 0.5)

data = generate_data_dict()

plot_improvement(data, ax1, ax2)

if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()

from util.helper import *
from collections import defaultdict
from math import sqrt
import numpy as np
import argparse
import re

exp_help = "Must be one of \'rtt\', \'bandwidth\', \'bdp\', or \'cwnds\'"

parser = argparse.ArgumentParser()
parser.add_argument('-e', dest='experiment', required=True, help=exp_help)
parser.add_argument('-b', '--baseline', dest='baseline_files', nargs='+',
                    required=True, help="Specify the files with which \
the experimental echoping results should be compared") 
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
#parser.add_argument('-n', dest="runs", type=int, help="Number of times \
#echoping was iterated to get the statistics for one run", required=True)

args = parser.parse_args()
num_files = len(args.files)

print args.baseline_files, args.files

experiment = 0
if args.experiment == 'rtt':
    experiment = 1
elif args.experiment == 'bandwidth':
    experiment = 2
elif args.experiment == 'bdp':
    experiment = 3
elif args.experiment == 'cwnds':
    experiment = 4
else:
    assert 0, exp_help

"""
Sample relevant lines from a file:
Minimum time: 0.063981 seconds (4001 bytes per sec.)
Maximum time: 0.067019 seconds (3820 bytes per sec.)
Average time: 0.065758 seconds (3893 bytes per sec.)
Standard deviation: 0.001189
Median time: 0.066370 seconds (3857 bytes per sec.)
"""
def parse_file(f):
    regex_num = '\d+\.?\d*'
    pattern_num = re.compile(regex_num)
    minimum = maximum = avg = std = median = 0
    with open(f) as opened:
        for l in opened:
            parts = l.split(":")
            if len(parts) != 2:
                continue
            nums = pattern_num.findall(parts[1])
            if parts[0] == 'Minimum time':
                minimum = float(nums[0]) * 1000
            elif parts[0] == 'Maximum time':
                maximum = float(nums[0]) * 1000
            elif parts[0] == 'Average time':
                avg = float(nums[0]) * 1000
            elif parts[0] == 'Standard deviation':
                std = float(nums[0]) * 1000
            elif parts[0] == 'Median time':
                median = float(nums[0]) * 1000
            elif parts[0] == 'cwnd':
                cwnd = int(nums[0])
            elif parts[0] == 'rtt':
                rtt = int(nums[0])
            elif parts[0] == 'bandwidth':
                bandwidth = int(nums[0])
            elif parts[0] == 'bdp':
                bdp = int(nums[0])
    
    return minimum, maximum, avg, std, median, cwnd, rtt, bandwidth, bdp

def plot_improvement(ax_abs, ax_percent):
    width = 0.35
    baseline = list()
    abs_list = list()
    percent_list = list()
    labels = list()
        
    for (base_f, f) in zip(args.baseline_files, args.files):
        b_min, b_max, b_avg, b_std, b_median, b_cwnd, b_rtt, b_bandwidth,\
            b_bdp = parse_file(base_f)
        minimum, maximum, avg, std, median, cwnd, rtt, bandwidth, bdp = \
            parse_file(f) 
        print minimum, maximum, avg, std, median, cwnd, rtt, bandwidth, bdp
        
        #diff_std = sqrt((b_std**2 + std**2)/args.runs)
        abs_list.append(b_avg - avg)
        percent_list.append((b_avg - avg) / b_avg)

        if experiment == 1:
            labels.append('%d' % rtt)
        elif experiment == 2:
            labels.append('%d' % bandwidth)
        elif experiment == 3:
            labels.append('%d' % bdp)
        elif experiment == 4:
            labels.append('%d' % cwnd)
        
    ind = np.arange(num_files)
    rects1 = ax_abs.bar(ind+width, abs_list, width, color='r') #, yerr=abs_err)
    rects2 = ax_percent.bar(ind+2*width, percent_list, width, color='b')
                            #, yerr=percent_err) 
    ax_abs.set_xticks(ind+2*width)
    ax_abs.set_xticklabels( tuple(labels) )
    ax_abs.legend( (rects1[0], rects2[0]),
                   ('Absolute Improvement','Percentage Improvement'),
                   loc=9)

m.rc('figure', figsize=(16, 6))
fig = plt.figure()

ax1 = fig.add_subplot(1, 1, 1)

if experiment == 1:
    ax1.set_xlabel("RTT (msec)")
elif experiment == 2:
    ax1.set_xlabel("Bandwidth (Kbps)")
elif experiment == 3:
    ax1.set_xlabel("BDP (Bytes)")
elif experiment == 4:
    ax1.set_xlabel("Cwnd")

ax1.set_ylabel("Improvement (ms)", color="r")
ax1.set_yscale("log")
ax1.grid(True, which='major', linestyle='-')
ax1.set_axisbelow(True)
ax1.set_ylim(1, 10000)

#http://matplotlib.sourceforge.net/examples/api/two_scales.html#api-two-scales
ax2 = ax1.twinx()
ax2.set_ylabel("Percentage Improvement",color="b")
ax2.set_yscale("linear")
ax2.set_ylim(0, 1)

plot_improvement(ax1, ax2)

if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()

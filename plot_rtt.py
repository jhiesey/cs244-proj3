from util.helper import *
from collections import defaultdict
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', dest="port", default='5001')
parser.add_argument('-f', dest="files", nargs='+', required=True)
parser.add_argument('-o', '--out', dest="out", default=None)
parser.add_argument('-H', '--histogram', dest="histogram",
                    help="Plot histogram of sum(cwnd_i)",
                    action="store_true",
                    default=False)

args = parser.parse_args()

def first(lst):
    return map(lambda e: e[0], lst)

def second(lst):
    return map(lambda e: e[1], lst)

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
    num_pattern = re.compile(regex_num)
    minimum = maximum = avg = std = median = 0
    with open(f) as opened:
        for l in opened:
            parts = l.split(":")
            if len(parts) != 2:
                continue
            nums = num_pattern.findall(parts[1])
            num = float(nums[0])
            if parts[0] == 'Minimum time':
                minimum = num
            elif parts[0] == 'Maximum time':
                maximum = num
            elif parts[0] == 'Average time':
                avg = num
            elif parts[0] == 'Standard deviation':
                std = num
            elif parts[0] == 'Median time':
                median = num
    
    return minimum, maximum, avg, std, median
'''
added = defaultdict(int)
events = []
'''
def plot_abs_improvement(ax):
    global events
    for f in args.files:
        #times, cwnds = parse_file(f)
        minimum, maximum, avg, std, median = parse_file(f)
        print minimum, maximum, avg, std, median
        '''
        for port in sorted(cwnds.keys()):
            t = times[port]
            cwnd = cwnds[port]

            events += zip(t, [port]*len(t), cwnd)
            ax.plot(t, cwnd)
            
    events.sort()
'''

def plot_percent_improvement(ax):
    pass

total_cwnd = 0
cwnd_time = []

min_total_cwnd = 10**10
max_total_cwnd = 0
totalcwnds = []

m.rc('figure', figsize=(16, 6))
fig = plt.figure()
plots = 1
'''
if args.histogram:
    plots = 2
'''

ax1 = fig.add_subplot(1, plots, 1)
plot_abs_improvement(ax1)
'''
for (t,p,c) in events:
    if added[p]:
        total_cwnd -= added[p]
    total_cwnd += c
    cwnd_time.append((t, total_cwnd))
    added[p] = c
    totalcwnds.append(total_cwnd)

ax1.plot(first(cwnd_time), second(cwnd_time), lw=2, label="$\sum_i W_i$")
ax1.legend()
ax1.set_xlabel("RTT")
ax1.set_ylabel("Improvement (ms)", color="r")
ax1.set_yscale("log")
#ax1.set_title("") #original has no title

#http://matplotlib.sourceforge.net/examples/api/two_scales.html#api-two-scales
ax2 = ax1.twinx()
ax2.set_ylabel("Percentage Improvement",color="b')
ax2.set_yscale("linear")
# plot on ax2 using ax2.plot(t, data_improvement)

if args.histogram:
    axHist = fig.add_subplot(1, 2, 2)
    n, bins, patches = axHist.hist(totalcwnds, 50, normed=1, facecolor='green', alpha=0.75)

    axHist.set_xlabel("bins (KB)")
    axHist.set_ylabel("Fraction")
    axHist.set_title("Histogram of sum(cwnd_i)")
'''
if args.out:
    print 'saving to', args.out
    plt.savefig(args.out)
else:
    plt.show()

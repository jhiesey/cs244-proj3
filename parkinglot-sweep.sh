#!/bin/bash

# Exit on any failure
set -e

# Check for uninitialized variables
set -o nounset

ctrlc() {
	killall -9 python
	mn -c
	exit
}

trap ctrlc SIGINT

start=`date`
exptid=`date +%b%d-%H:%M`
rootdir=latency-$exptid
bw=100

# Note: you need to make sure you report the results
# for the correct port!
# In this example, we are assuming that each
# client is connected to port 2 on its switch.

for cwnd in 1 2 5 10 15 20; do
    dir=$rootdir/cwnd$cwnd
    python parkinglot.py --bw $bw \
        --cwnd $cwnd \
        --dir $dir \
        -t 60 \
    # python util/plot_rate.py --rx \
    #     --maxy $bw \
    #     --xlabel 'Time (s)' \
    #     --ylabel 'Rate (Mbps)' \
    #     -i 's.*-eth2' \
    #     -f $dir/bwm.txt \
    #     -o $dir/rate.png
    # python util/plot_tcpprobe.py \
    #     -f $dir/tcp_probe.txt \
    #     -o $dir/cwnd.png
done

# for n in 1 2 3 4 5; do
#     dir=$rootdir/n$n
#     python parkinglot.py --bw $bw \
#         --dir $dir \
#         --delay 150\
#         -t 60 \
#         -n $n
#     python util/plot_rate.py --rx \
#         --maxy $bw \
#         --xlabel 'Time (s)' \
#         --ylabel 'Rate (Mbps)' \
#         -i 's.*-eth2' \
#         -f $dir/bwm.txt \
#         -o $dir/rate.png
#     python util/plot_tcpprobe.py \
#         -f $dir/tcp_probe.txt \
#         -o $dir/cwnd.png
# done

echo "Started at" $start
echo "Ended at" `date`
echo "Output saved to $rootdir"

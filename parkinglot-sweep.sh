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

mkdir $rootdir

rtt_files_baseline=
rtt_files=

for rtt in 20 50 100 200 500 1000 3000; do
    dir=$rootdir/rtt$rtt
    dir_baseline=$rootdir/rtt$rtt-baseline
    rtt_files_baseline=$rtt_files_baseline\ $dir_baseline/echoping.txt
    rtt_files=$rtt_files\ $dir/echoping.txt
    # Baseline
    python parkinglot.py --bw $bw \
        --cwnd 2 \
        --rtt $rtt \
        --dir $dir_baseline \
        -t 60 \
    # Increased cwnd
    python parkinglot.py --bw $bw \
        --cwnd 10 \
        --rtt $rtt \
        --dir $dir \
        -t 60 \

done

# Create RTT plot
python plot_results.py -e rtt -o result.png -b $rtt_files_baseline -f $rtt_files

#for cwnd in 1 2 5 10 15 20; do
#    echo $cwnd >> $rootdir/cwnds.txt
#    dir=$rootdir/cwnd$cwnd
#    python parkinglot.py --bw $bw \
#        --cwnd $cwnd \
#        --dir $dir \
#        -t 60 \
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
#done

echo "Started at" $start
echo "Ended at" `date`
echo "Output saved to $rootdir"

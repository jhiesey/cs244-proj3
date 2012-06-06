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
bw=0.5

mkdir $rootdir

rtt_files_baseline=
rtt_files=

for rtt in 20 50 100 200; do # 500 1000 3000; do
    dir=$rootdir/rtt$rtt
    dir_baseline=$rootdir/rtt$rtt-baseline
    rtt_files_baseline=$rtt_files_baseline\ $dir_baseline/latency.txt
    rtt_files=$rtt_files\ $dir/latency.txt
    # Baseline
    python initcwnd.py --bw $bw \
        --cwnd 2 \
        --rtt $rtt \
        --dir $dir_baseline \
        -t 60 --hosts 10 # -l 1
    # Increased cwnd
    python initcwnd.py --bw $bw \
        --cwnd 10 \
        --rtt $rtt \
        --dir $dir \
        -t 60 --hosts 10 # -l 1

done

# Create RTT plot
python plot_results.py -e rtt -o result.png -b $rtt_files_baseline -f $rtt_files

echo "Started at" $start
echo "Ended at" `date`
echo "Output saved to $rootdir"

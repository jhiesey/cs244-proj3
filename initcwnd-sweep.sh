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

# rootdir=latency-$exptid-basecwnd
# bw=100
# 
# mkdir $rootdir

# for rtt in 20 50 100 200; do # 500 1000 3000; do
#     # dir=$rootdir/rtt$rtt
#     # dir_baseline=$rootdir/rtt$rtt-baseline
#     # rtt_files_baseline=$rtt_files_baseline\ $dir_baseline/latency.txt
#     # rtt_files=$rtt_files\ $dir/latency.txt
#     # Baseline
#     # python initcwnd.py --bw $bw \
#     #     --cwnd 2 \
#     #     --rtt $rtt \
#     #     --dir $rootdir \
#     #     -t 60 --hosts 10 # -l 1
#     # # Increased cwnd
#     # python initcwnd.py --bw $bw \
#     #     --cwnd 10 \
#     #     --rtt $rtt \
#     #     --dir $rootdir \
#     #     -t 60 --hosts 10 # -l 1
# 	
# 	for cwnd in 3 6 10 16 26 42; do
# 		python initcwnd.py --bw $bw \
# 		    --cwnd $cwnd \
# 		    --rtt $rtt \
# 		    --dir $rootdir \
# 		    -t 60 --hosts 1 -l 1
# 	done
# done
# 
# # Create RTT plot
# python plot_results2.py -o result.png -f $rootdir/
# 
# echo "Started at" $start
# echo "Ended at" `date`
# echo "Output saved to $rootdir"

# BASIC REPLICATION
rootdir=latency-$exptid-basecwnd
mkdir $rootdir
bw=100

for rtt in 20 50 100 200 500 1000 3000; do
	for cwnd in 3 10; do
		python initcwnd.py --bw $bw \
		    --cwnd $cwnd \
		    --rtt $rtt \
		    --dir $rootdir \
		    --hosts 1 --minsize 30000 --maxsize 30000 --numtests 10
		    # -t 60 --hosts 1 --minsize 7536 --maxsize 11943 --numtests 10
	done
done

# Create RTT plot
python plot_results2.py -o $rootdir/result.png -b 3 -p true -f $rootdir/

# # MORE CWNDS
# rootdir=latency-$exptid-multicwnd
# mkdir $rootdir
# bw=100
# 
# for rtt in 20 50 100 200 500 1000 3000; do
# 	for cwnd in 3 6 10 16 26 42; do
# 		python initcwnd.py --bw $bw \
# 		    --cwnd $cwnd \
# 		    --rtt $rtt \
# 		    --dir $rootdir \
# 		    --hosts 1 --maxsize 100000
# 	done
# done
# 
# # Create RTT plot
# python plot_results2.py -o $rootdir/result.png -f $rootdir/
# 
# # LOSSY LINK
# rootdir=latency-$exptid-lossy
# mkdir $rootdir
# bw=100
# 
# for rtt in 20 50 100 200 500 1000 3000; do
# 	for cwnd in 3 6 10 16 26 42; do
# 		python initcwnd.py --bw $bw \
# 		    --cwnd $cwnd \
# 		    --rtt $rtt \
# 		    --dir $rootdir \
# 		    --hosts 1 --maxsize 100000 --loss 10 --numtests 3
# 	done
# done
# 
# # Create RTT plot
# python plot_results2.py -o $rootdir/result.png -f $rootdir/
# 
# # SATURATED LINK
# rootdir=latency-$exptid-saturated
# mkdir $rootdir
# bw=1
# 
# for rtt in 20 50 100 200 500 1000 3000; do
# 	for cwnd in 3 6 10 16 26 42; do
# 		python initcwnd.py --bw $bw \
# 		    --cwnd $cwnd \
# 		    --rtt $rtt \
# 		    --dir $rootdir \
# 		    --hosts 1 --maxsize 100000 --hosts 10 --lambda 1
# 	done
# done
# 
# # Create RTT plot
# python plot_results2.py -o $rootdir/result.png -f $rootdir/


echo "Started at" $start
echo "Ended at" `date`
echo "Output saved to $rootdir"


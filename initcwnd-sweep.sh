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
		    # --hosts 1 --minsize 7536 --maxsize 11943 --numtests 10
	done
done

# Create RTT plot
python plot_results2.py -o $rootdir/result.png -b 3 -p -f $rootdir/
echo "Output saved to $rootdir"

# MORE CWNDS
rootdir=latency-$exptid-multicwnd
mkdir $rootdir
bw=100

for rtt in 20 50 100 200 500; do
	for cwnd in 3 6 10 16 26 42; do
		python initcwnd.py --bw $bw \
		    --cwnd $cwnd \
		    --rtt $rtt \
		    --dir $rootdir \
		    --hosts 1 --maxsize 100000
	done
done

# Create RTT plot
python plot_results2.py -o $rootdir/result.png -f $rootdir/
echo "Output saved to $rootdir"

# LOSSY LINK
rootdir=latency-$exptid-lossy
mkdir $rootdir
bw=100

for rtt in 20 50 100 200 500; do
	for cwnd in 3 6 10 16 26 42; do
		python initcwnd.py --bw $bw \
		    --cwnd $cwnd \
		    --rtt $rtt \
		    --dir $rootdir \
		    --hosts 1 --maxsize 100000 --loss 5 --numtests 3
	done
done

# Create RTT plot
python plot_results2.py -o $rootdir/result.png -f $rootdir/
echo "Output saved to $rootdir"

# SATURATED LINK
rootdir=latency-$exptid-saturated
mkdir $rootdir
bw=0.5

for rtt in 20 50 100 200 500; do
	for cwnd in 3 6 10 26; do
		python initcwnd.py --bw $bw \
		    --cwnd $cwnd \
		    --rtt $rtt \
		    --dir $rootdir \
		    --hosts 1 --maxsize 100000 --hosts 10 --lambda 1
	done
done

# Create RTT plot
python plot_results2.py -o $rootdir/result.png --ylim 6500 -f $rootdir/
echo "Output saved to $rootdir"

echo "Started at" $start
echo "Ended at" `date`

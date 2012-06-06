#!/usr/bin/env

import argparse
import random
import subprocess
import time

parser = argparse.ArgumentParser(description="Congesiton window client")

parser.add_argument('--filename',
                    help="Filename to store outputs",
                    default="results")
                    
parser.add_argument('--server',
                    dest='server',
                    type=str,
                    help="Server IP",
                    default=10)
 
parser.add_argument('--hnum',
                    dest='hostnum',
                    type=int,
                    help="Host number",
                    default=1)
                
parser.add_argument('--lambda', '-l',
                    dest='lambd',
                    type=float,
                    help="Poisson parameter",
                    default=None)
                    
parser.add_argument('--numtests',
                    dest='numtests',
                    type=int,
                    help="Number of tests",
                    default=1)
                    
parser.add_argument('--minsize',
                    type=int,
                    help="Minimum file size for experiments",
                    default=0)

parser.add_argument('--maxsize',
                    type=int,
                    help="Maximum file size for experiments",
                    default=1000000)

args = parser.parse_args()

port = 5001
for size in [300, 475, 754, 1194, 1893, 3000, 4755, 7536, 11943, 18929, 30000, 47547, 75357, 119432, 189287, 3000000]:
    if size < args.minsize:
        continue
    if size > args.maxsize:
        break
    
    command = "curl -o /dev/null -w '%%{time_total}\\n' %s:%d/testfiles/test%d >> %s" % (args.server, port, size, args.filename)
    for j in range(args.numtests):
        print(command)
        if args.lambd is not None:
            stopTime = time.time() + random.expovariate(args.lambd)
            subprocess.call(command, shell=True)
            waitTime = stopTime - time.time()
            if waitTime > 0:
                time.sleep(waitTime)
        else:
            subprocess.call(command, shell=True)
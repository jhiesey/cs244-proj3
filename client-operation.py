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
                    default=10)

args = parser.parse_args()

size = 30
port = 5001
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
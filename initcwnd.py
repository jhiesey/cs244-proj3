#!/usr/bin/python

"CS244 Assignment 3: Initial Congestion Window"

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, output
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange, custom, quietRun, dumpNetConnections
from mininet.cli import CLI

from time import sleep, time
from multiprocessing import Process
from subprocess import Popen
import subprocess
import termcolor as T
import argparse
import threading
import random

import sys
import os
from util.monitor import monitor_devs_ng

def cprint(s, color, cr=True):
    """Print in color
       s: string to print
       color: color to use"""
    if cr:
        print T.colored(s, color)
    else:
        print T.colored(s, color),

parser = argparse.ArgumentParser(description="Congestion window tests")

parser.add_argument('--dir',
                    help="Directory to store outputs",
                    default="results")

parser.add_argument('--cli',
                    action='store_true',
                    help='Run CLI for topology debugging purposes')

parser.add_argument('--time', '-t',
                    dest="time",
                    type=int,
                    help="Duration of the experiment.",
                    default=60)
                    
parser.add_argument('--cwnd', '-c',
                    dest="cwnd",
                    type=int,
                    help="Congestion window.",
                    default=2)

parser.add_argument('--rtt', '-r', dest="rtt", type=int,
                    help="rtt b/w the hosts in ms", default=200)

parser.add_argument('--bw', '-b',
                    type=float,
                    help="Bandwidth of network links",
                    required=True)
                    
parser.add_argument('--numtests',
                    dest='numtests',
                    type=int,
                    help="Number of tests",
                    default=10)
 
parser.add_argument('--hosts',
                    dest='hosts',
                    type=int,
                    help="Number of hosts",
                    default=1)
                
parser.add_argument('--lambda', '-l',
                    dest='lambd',
                    type=float,
                    help="Poisson parameter",
                    default=None)

parser.add_argument('--loss',
                    dest='loss',
                    type=float,
                    help="Link loss",
                    default=0)

# Expt parameters
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class InitCwndTopo(Topo):
    "InitCwnd Topology"

    def __init__(self, n=1, cpu=.1, bw=10, delay=100,
                 max_queue_size=None, **params):
        """InitCwnd topology with one receiver
           and n clients.
           n: number of clients
           cpu: system fraction for each host
           bw: link bandwidth in Mb/s
           delay: link delay (e.g. 10ms)"""

        # Initialize topo
        Topo.__init__(self, **params)
        assert(n > 0)
        self.n = n

        # Host and link configuration
        hconfig = {'cpu': cpu}
        lconfig = {'bw': bw, 'delay': ('%sms' % delay),
                   'max_queue_size': max_queue_size, 'loss': args.loss}
                   
        serverSwitch = self.add_switch('s1')
        clientSwitch = self.add_switch('s2')
        
        self.add_link(serverSwitch, clientSwitch, 0, 0, **lconfig)
        
        for i in range(1, args.hosts + 1):
            server = self.add_host('server' + str(i), **hconfig)
            client = self.add_host('client' + str(i), **hconfig)
        
            self.add_link(server, serverSwitch, 0, i)
            self.add_link(client, clientSwitch, 0, i)
        
def waitListening(client, server, port):
    "Wait until server is listening on port"
    if not 'telnet' in client.cmd('which telnet'):
        raise Exception('Could not find telnet')
    cmd = ('sh -c "echo A | telnet -e A %s %s"' %
           (server.IP(), port))
    while 'Connected' not in client.cmd(cmd):
        output('waiting for', server,
               'to listen on port', port, '\n')
        sleep(.5)

# def progress(t):
#     while t > 0:
#         cprint('  %3d seconds left  \r' % (t), 'cyan', cr=False)
#         t -= 1
#         sys.stdout.flush()
#         sleep(1)
#     print

def start_tcpprobe():
    os.system("rmmod tcp_probe > /dev/null; modprobe tcp_probe full=1;")
    Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" % args.dir, shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe > /dev/null;")

def get_ip_configs(net):
    server = net.getNodeByName('server1')
    client = net.getNodeByName('client1')

    server.sendCmd('ip route')
    client.sendCmd('ip route')
    return "Server Config: %s\nClient Config: %s" %\
        (server.waitOutput(), client.waitOutput())
    

def run_initcwnd_expt(net, cwnd):
    "Run experiment"

    seconds = args.time

    # Start the bandwidth and cwnd monitors in the background
    monitor = Process(target=monitor_devs_ng, 
            args=('%s/bwm.txt' % args.dir, 1.0))
    monitor.start()
    start_tcpprobe()

    # Set up servers
    for i in range(1, args.hosts + 1):
        # Get receiver and clients
        server = net.getNodeByName('server' + str(i))
        client = net.getNodeByName('client' + str(i))
    
        # Save original ip route configs
        server.sendCmd('ip route')
        origServerRoute = server.waitOutput()
        client.sendCmd('ip route')
        origClientRoute = client.waitOutput()
        print (origServerRoute, origClientRoute)
    
        server.cmd('ip route replace %s initcwnd %d' % (origServerRoute.rstrip(), cwnd))
        server.cmd('ip route replace %s initrwnd %d' % (origClientRoute.rstrip(), 50))
    
        # sleep(60)
        print get_ip_configs(net)
    
        server.cmd('sysctl -w net.ipv4.tcp_no_metrics_save=1')
        server.cmd('sysctl -w net.ipv4.route.flush=1')
    
        # Start the receiver
        port = 5001
        command = 'python -m SimpleHTTPServer %d &' % port
        print(command)
        server.cmd(command)
    
        server.sendCmd('ifconfig')
        print('server: %s' % server.waitOutput())
        
    sleep(1)
    # waitListening(sender1, recvr, port)            
    
    clients = []    
    for i in range(1, args.hosts + 1):
        client = net.getNodeByName('client' + str(i))
        client = net.getNodeByName('client' + str(i))
        latencyFile = "host-%d-cwnd-%d-rtt-%d.txt" % (i, args.cwnd, args.rtt)
        
        if args.lambd is not None:
            client.sendCmd('python client-operation.py --filename %s/%s --server %s --hnum %d --lambda %f --numtests %d' % (args.dir, latencyFile, server.IP(), i, args.lambd, args.numtests))
        else:
            client.sendCmd('python client-operation.py --filename %s/%s --server %s --hnum %d --numtests %d' % (args.dir, latencyFile, server.IP(), i, args.numtests))
        clients.append(client)

    for client in clients:
        print(client.waitOutput())

    latencyFile = "cwnd-%d-rtt-%d.txt" % (args.cwnd, args.rtt)
    # Have client print parameters into output
    subprocess.call("echo \"cwnd: %d\" >> %s/%s" % (args.cwnd, args.dir, latencyFile), shell=True)
    subprocess.call("echo \"rtt: %d\" >> %s/%s" % (args.rtt, args.dir, latencyFile), shell=True)
    subprocess.call("echo \"bandwidth: %d\" >> %s/%s" % (args.bw, args.dir, latencyFile), shell=True)
    subprocess.call("echo \"bdp: %d\" >> %s/%s" % (args.bw * args.rtt, args.dir, latencyFile), shell=True)
        
    # Combine results
    subprocess.call("cat %s/host-*-%s >> %s/%s" % (args.dir, latencyFile, args.dir, latencyFile), shell=True)

    # Shut down monitors
    monitor.terminate()
    stop_tcpprobe()

def check_prereqs():
    "Check for necessary programs"
    prereqs = ['telnet', 'bwm-ng', 'iperf', 'ping']
    for p in prereqs:
        if not quietRun('which ' + p):
            raise Exception((
                'Could not find %s - make sure that it is '
                'installed and in your $PATH') % p)

def main():
    "Create and run experiment"
    start = time()

    topo = InitCwndTopo(1, cpu=.15, bw=args.bw, delay=args.rtt/2,
                          max_queue_size=200)

    # host = custom(CPULimitedHost, cpu=.15)  # 15% of system bandwidth
    # link = custom(TCLink, bw=args.bw,
    #               max_queue_size=200)
    link = custom(TCLink)

    # net = Mininet(topo=topo, host=host, link=link)
    
    net = Mininet(topo=topo, link=link)

    net.start()

    cprint("*** Dumping network connections:", "green")
    dumpNetConnections(net)

    cprint("*** Testing connectivity", "blue")

    net.pingAll()

    if args.cli:
        # Run CLI instead of experiment
        CLI(net)
    else:
        cprint("*** Running experiment", "magenta")
        run_initcwnd_expt(net, args.cwnd)

    net.stop()
    end = time()
    os.system("killall -9 bwm-ng")
    cprint("Experiment took %.3f seconds" % (end - start), "yellow")

if __name__ == '__main__':
    check_prereqs()
    main()


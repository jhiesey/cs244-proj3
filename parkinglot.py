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
import termcolor as T
import argparse

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

# parser.add_argument('-n',
#                     type=int,
#                     help=("Number of senders in the parking lot topo."
#                     "Must be >= 1"),
#                     required=True)

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

# parser.add_argument('--delay', '-d',
#                     dest="delay",
#                     type=float,
#                     help="Latency on the link in ms",
#                     default=100)

# Expt parameters
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class ParkingLotTopo(Topo):
    "Parking Lot Topology"

    def __init__(self, n=1, cpu=.1, bw=10, delay=100,
                 max_queue_size=None, **params):
        """Parking lot topology with one receiver
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
                   'max_queue_size': max_queue_size }
                   
        server = self.add_host('server', **hconfig)
        client = self.add_host('client', **hconfig)
        
        self.add_link(server, client, 0, 0, **lconfig)
        

        # # Create the actual topology
        # receiver = self.add_host('receiver')
        # 
        # # Switch ports 1:uplink 2:hostlink 3:downlink
        # uplink, hostlink, downlink = 1, 2, 3
        # 
        # prev_node = receiver # The node for the next switch's uplink to connect to
        # upstream_port = 0 # The port for the next switch's uplink to connect to
        # for i in range(1, n + 1):
        #     # Add the switch and host
        #     si = self.add_switch('s' + str(i))
        #     hi = self.add_host('h' + str(i), **hconfig)
        # 
        #     # Connect the upstream side
        #     self.add_link(prev_node, si, port1=upstream_port, port2=uplink, **lconfig)
        # 
        #     # Connect the host
        #     self.add_link(hi, si, port1=0, port2=hostlink, **lconfig)
        # 
        #     # The next switch will connect to this switch
        #     prev_node = si
        #     upstream_port = downlink

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
    os.system("rmmod tcp_probe &>/dev/null; modprobe tcp_probe;")
    Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" % args.dir, shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe &>/dev/null;")

def run_parkinglot_expt(net, cwnd):
    "Run experiment"

    seconds = args.time

    # Start the bandwidth and cwnd monitors in the background
    monitor = Process(target=monitor_devs_ng, 
            args=('%s/bwm.txt' % args.dir, 1.0))
    monitor.start()
    start_tcpprobe()

    # Get receiver and clients
    server = net.getNodeByName('server')
    client = net.getNodeByName('client')
    
    server.sendCmd('ip route')
    origRoute = server.waitOutput()
    print (origRoute)
    
    server.cmd('ip route replace %s initcwnd %d' % (origRoute.rstrip(), cwnd))
    
    # sleep(60)
    
    server.sendCmd('ip route')
    print(server.waitOutput())
    
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
    
    # Have client print parameters into output
    client.cmd("echo \"cwnd: %d\" >> %s/echoping.txt" % (args.cwnd, args.dir))
    client.cmd("echo \"rtt: %d\" >> %s/echoping.txt" % (args.rtt, args.dir))
    client.cmd("echo \"bandwidth: %d\" >> %s/echoping.txt" % (args.bw, args.dir))
    client.cmd("echo \"bdp: %d\" >> %s/echoping.txt" % (args.bw * args.rtt, args.dir))

    size = 30
    command = "curl -o TEST.OUT -w '%%{time_total}\\n' %s:%d/testfiles/test%d >> %s/echoping.txt" % (server.IP(), port, size, args.dir)
    for i in range(10):
        print(command)
        client.cmd(command)
        sleep(1)
        
    # command = 'echoping -n 10 -h /testfiles/test%s %s:%d > %s/echoping.txt' % (size, server.IP(), port, args.dir)
    # print(command)
    # client.cmd(command)
    
    client.sendCmd('ifconfig')
    print('client: %s' % client.waitOutput())

    # Hint: Use sendCmd() and waitOutput() to start iperf and wait for them to finish
    # iperf command to start flow: 'iperf -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name)
    # Hint (not important): You may use progress(t) to track your experiment progress
    # for i in range(1,n+1):
    #     node_name = 'h%d' % i
    #     hi = net.getNodeByName(node_name)
    #     hi.sendCmd('iperf -Z reno -c %s -p %s -t %d -i 1 -yc > %s/iperf_%s.txt' % (recvr.IP(), 5001, seconds, args.dir, node_name))
    # 
    # for i in range(1,n+1):
    #     hi = net.getNodeByName('h%d' % i)
    #     hi.waitOutput()
    # 
    # recvr.cmd('kill %iperf')

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

    topo = ParkingLotTopo(1, cpu=.15, bw=args.bw, delay=args.rtt/2,
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
        run_parkinglot_expt(net, args.cwnd)

    net.stop()
    end = time()
    os.system("killall -9 bwm-ng")
    cprint("Experiment took %.3f seconds" % (end - start), "yellow")

if __name__ == '__main__':
    check_prereqs()
    main()


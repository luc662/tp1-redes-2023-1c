from mininet.topo import Topo
from mininet.link import TCLink

hosts_num = 40
LOSS = 10

class MyTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)
        hosts = {}

        # Create hosts
        for host in range(hosts_num):
            hosts[f'h{host}'] = self.addHost(f'h{host}')

        # Create switch
        switch = self.addSwitch(f's1')

        for host in hosts:
            self.addLink(hosts[host], switch, cls=TCLink, loss=LOSS)

topos = {'customTopo': MyTopo }
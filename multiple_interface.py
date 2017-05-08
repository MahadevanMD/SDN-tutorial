"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.node import Host,Node
from mininet.util import ensureRoot, waitListening
from mininet.log import info, warn, output
class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        Host1 = self.addHost( 'h1' )
	Host2 = self.addHost( 'h2' )
	Host3 = self.addHost( 'h3' )
	Host4 = self.addHost( 'h4' )

        Switch1 = self.addSwitch( 's1' )
        Switch2 = self.addSwitch( 's2' )
	Switch3 = self.addSwitch( 's3' )

        # Add links
        self.addLink( Switch1, Switch2 )
        self.addLink( Switch1, Switch3 )
        self.addLink( Switch2, Host1 ,addr2='00:00:00:00:00:01')
	self.addLink( Switch2, Host2 ,addr2='00:00:00:00:00:02')
	self.addLink( Switch3, Host3 ,addr2='00:00:00:00:00:03')
	self.addLink( Switch3, Host4 ,addr2='00:00:00:00:00:04')
	
	


topos = { 'mytopo': ( lambda: MyTopo() ) }

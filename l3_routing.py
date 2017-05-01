# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ether_types


class l3Routing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(l3Routing, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        if dpid == 1:
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.1', ipv4_dst = '10.0.0.3', eth_type=0x0800), [parser.OFPActionOutput(1)])
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.3', ipv4_dst = '10.0.0.1', eth_type=0x0800), [parser.OFPActionOutput(3)])

        elif dpid == 2:
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.1', ipv4_dst = '10.0.0.3', eth_type=0x0800), [parser.OFPActionOutput(2)])
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.3', ipv4_dst = '10.0.0.1', eth_type=0x0800), [parser.OFPActionOutput(1)])

	elif dpid == 3:
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.1', ipv4_dst = '10.0.0.3', eth_type=0x0800), [parser.OFPActionOutput(2)])
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.3', ipv4_dst = '10.0.0.1', eth_type=0x0800), [parser.OFPActionOutput(1)])

	elif dpid == 6:
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.1', ipv4_dst = '10.0.0.3', eth_type=0x0800), [parser.OFPActionOutput(3)])
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.3', ipv4_dst = '10.0.0.1', eth_type=0x0800), [parser.OFPActionOutput(1)])
	elif dpid == 9:
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.1', ipv4_dst = '10.0.0.3', eth_type=0x0800), [parser.OFPActionOutput(3)])
           self.add_flow(datapath, 1, parser.OFPMatch(ipv4_src = '10.0.0.3', ipv4_dst = '10.0.0.1', eth_type=0x0800), [parser.OFPActionOutput(1)])

	


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']


        pkt = packet.Packet(msg.data)
        pkt_arp = pkt.get_protocols(arp.arp)

        if pkt_arp:

            dpid = datapath.id
            self.mac_to_port.setdefault(dpid, {})

            out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]

            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            print 'arp'
            datapath.send_msg(out)
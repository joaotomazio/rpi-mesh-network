import socket
import json
from time import time
from threading import Thread
import struct

PORT = 3000

session = None

##########################################################
# Name:     setup
# Args:     -
# Return:   -
# Desc:     Socket setup for comunication.
##########################################################
def setup():
    global session
    MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
    addrinfo = socket.getaddrinfo(MYGROUP_6, None)[0]

    session = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    session.bind(('', PORT))
    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    mreq = group_bin + struct.pack('@I', 0)
    session.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
    session.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 1)
    session.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, 10)

##########################################################
# Name:     send
# Args:     msg - Message to be sent.
#           table - Routing table
# Return:   -
# Desc:     Socket send message.
##########################################################
def send(msg, table):
    global session
    global PORT
    found = False

    if msg['to'] == 'all':
        ip = "ff02::1%wlan0"
        found = True
    else:
        for entry in table:
            if entry['to'] == msg['to']:
                found = True
                ip = entry['via']
                break
    
    if found:
        msg = json.dumps(msg)
        try:
            session.sendto(msg, (ip, PORT))
        except:
            print 'Error Sending Message'
    else:
        print 'No Route to Host'

##########################################################
# Name:     receive
# Args:     -
# Return:   data - message received.
# Desc:     Socket receive message.
##########################################################
def receive():
    data, address = session.recvfrom(100000)
    data = json.loads(data)
    return data

##########################################################
# Name:     shutdown
# Args:     -
# Return:   -
# Desc:     Socket shutdown.
##########################################################
def shutdown():
    global session
    try:
        session.shutdown(socket.SHUT_RDWR)
    except socket.error:
        print 'Error Closing Socket'

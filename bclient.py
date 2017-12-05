import sys, requests, os
import hashlib, urllib
import bencode
import socket
import struct

BUFFER_SIZE = 2**14

with open(sys.argv[1], 'rb') as f:
    torrent = f.read()
    metadata = bencode.bdecode(torrent)

#connect to the tracker via HTTP GET request
#in the format tracker_url+info_hash=info_hash?port=port?etc
#look @ bittorrent specification for full details
announcer = metadata['announce']
info = metadata['info']
info_hash20 = hashlib.sha1(bencode.bencode(info)).digest()
info_hash = urllib.quote_plus(info_hash20)
peer_id20 = os.urandom(20)
peer_id = urllib.quote_plus(peer_id20)
uploaded = 0 
downloaded = 0 
left = metadata['info']['length']
compact = 1
event = "started"

for port in range(6881, 6890):
    tracker_url = "{}?info_hash={}&peer_id={}&port={}&uploaded={}&downloaded={}&left={}&compact={}&event={}".format(announcer, info_hash, peer_id, port, uploaded, downloaded, left, compact, event)
    tracker = requests.get(tracker_url)
    print port, tracker.status_code
    if tracker.status_code == 200:
        tracker_response = tracker.text
        break

tracker_response = bencode.bdecode(tracker.text)
peers = tracker_response['peers']
peers = [peers[i:i+6] for i in range(0, len(peers), 6)]
peers = [(x[:4], x[-2:]) for x in peers]
peer_list = []
for p in peers:
    pip = [str(ord(x)) for x in p[0]]
    pip = ".".join(pip)
    pport = [ord(x) for x in p[1]]
    pport = sum([pport[-i+1]*256**i for i in range(len(pport))])
    peer_list.append((pip,pport))

#do handshake
peer = peer_list[0]
print peer
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#SET TIMEOUTS / MAKE CONNECTING CLEANER / USE TRY EXCEPT BLOCKS
s.connect(peer)
pstr = "BitTorrent protocol"
pstrlen = len(pstr)
handshake = "".join([chr(pstrlen), pstr, chr(0)*8, info_hash20, peer_id20])
s.send(handshake)
peer_handshake = s.recv(68)

info_index = len(chr(pstrlen) + pstr) + 8

if not info_hash20 == peer_handshake[info_index:info_index+20]:
    print "bad info hash"
    exit

#successful handshake, send interested
'''
#message parsing to figure out what file to get
data = s.recv(5)
m = struct.pack(">IB", 1, 1)
messages = struct.unpack("B" * len(data), data)
print messages
'''

#***right now this is all wild speculation and we have no idea if it works or not. but ive formatted what i think the messages should be and we are sending an interested message and a request. after sending interested, we get a large field of 255, which we think is the peer telling us that it has all the pieces, and then after request we get another tuple -- maybe an unchoke? looks like an unchoke.*** 
#we recommend checking out section 4.4 in the new tutorial bri sent.  

#messages:
not_interested = struct.pack(">IB", 0001, 3)
interested = struct.pack(">IB", 0001, 2)
unchoke = struct.pack(">IB", 0001, 1)
choke = struct.pack(">IB", 0001, 0)
request = struct.pack(">IBBBI", 0013, 6, 1, 1, 16)

#send interested message
print "-> interested"
s.send(interested)

buf = b''
#while True: #continue to receive messages
for x in range(4): #just to test 4 times
    response = s.recv(BUFFER_SIZE)
    buf += response
    while True: #parse through the messages received
        if len(buf) < 5: #not enough info to parse
            break

        length = struct.unpack(">I", buf[:4])[0]
        print "length:{}".format(length)
        
        if len(buf) < length: #payload not long enough
            break

        def get_payload(buf):
            return buf[:4+length]
        def read_buffer(buf):
            return buf[4+length:]

        if length == 0:
            print "<- keep alive"
            buf = read_buffer(buf)            
        
        # parse messages
        
        mid = struct.unpack(">B", buf[4:5])[0]
        print "message id:{}".format(mid)

        if mid == 0:
            print "<- choke"
            buf = read_buffer(buf)
        elif mid == 1:
            print "<- unchoke"
            buf = read_buffer(buf)
        elif mid == 2:
            print "<- interested"
            buf = read_buffer(buf)
        elif mid == 3:
            print "<- not interested"
            buf = read_buffer(buf)
        elif mid == 4:
            print "<- have"
            buf = buf[5:] #have has fixed message length
            buf = read_buffer(buf)
        elif mid == 5:
            print "<- bitfield"
            bitfield = buf[5:5+length-1]
            # should update some internal bitfield somewhere to keep track of pieces
            print "Bitfield: {}".format(bitfield)
            buf = read_buffer(buf)
            s.send(interested) #probably not the right thing to send
        elif mid == 6:
            print "<- request"
            buf = read_buffer(buf)
        elif mid == 7:
            print "<- piece"
            #need to download the files!
        else:
            print "unknown message id:{}".format(mid)

#write data to file
s.close()

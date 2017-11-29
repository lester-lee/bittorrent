import sys, requests, os
import hashlib, urllib
import bencode
import socket
import struct

BUFFER_SIZE = 1024

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
peer_handshake = s.recv(4096)

info_index = len(chr(pstrlen) + pstr) + 8

if not info_hash20 == peer_handshake[info_index:info_index+20]:
    print "bad info hash"
    exit
    
#message parsing to figure out what file to get
data = s.recv(5)
m = struct.pack(">IB", 1, 1)
messages = struct.unpack("B" * len(data), data)
print messages

#right now we are getting the bitfield message
#to Mary: figure out how to send interested message / receive more messages
#and possibly how to start receiving data to download from the peer



#write data to file
s.close()


import sys, requests, os
import hashlib, urllib
import bencode
import socket

with open(sys.argv[1], 'rb') as f:
    torrent = f.read()
    metadata = bencode.bdecode(torrent)

    
#connect to the tracker via HTTP GET request
#in the format tracker_url+info_hash=info_hash?port=port?etc
#look @ bittorrent specification for full details
announcer = metadata['announce']
info = metadata['info']
info_hash = hashlib.sha1(bencode.bencode(info)).digest()
info_hash = urllib.quote_plus(info_hash)
peer_id = os.urandom(20)
peer_id = urllib.quote_plus(peer_id)
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

#decode the tracker response (step 5 of tutorial)
tracker_response = bencode.bdecode(tracker.text)
peers = tracker_response['peers']
peers = [peers[i:i+6] for i in range(0, len(peers), 6)]
peers = [(x[:4], x[4:]) for x in peers]
# need to turn each peer byte into ipaddress + port combo
print peers

peer = "127.0.0.1:8888" #pretend this is successful
#connect to peer
#do handshake

#message parsing to figure out what file to get

#write data to file

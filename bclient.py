import sys
import struct
import torrent, peer

BUFFER_SIZE = 2**14

tor = torrent.Torrent(sys.argv[1])
tracker = tor.generate_tracker()
peers = tracker.peers

peer = peer.Peer(tor, peers[0])
peer.download()

#write data to file
s.close()

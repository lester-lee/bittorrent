import sys
import torrent, peer, downloader
import math

tor = torrent.Torrent(sys.argv[1])
downloader = downloader.Downloader(tor)
tracker = tor.generate_tracker()
peers = tracker.peers

peer = peer.Peer(tor, downloader,peers[0])
peer.download()

#write data to file
s.close()

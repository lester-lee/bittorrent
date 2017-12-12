import sys
import torrent, peer, downloader
import math
import threading

tor = torrent.Torrent(sys.argv[1])
downloader = downloader.Downloader(tor)
tracker = tor.generate_tracker()
peers = tracker.peers

threads = []

for p in peers:
    print p
    peer_obj = peer.Peer(tor, downloader, p, verbose=False)
    t = threading.Thread(group=None,
                         target=peer_obj.download, name=None)
    threads.append(t)
    t.start()



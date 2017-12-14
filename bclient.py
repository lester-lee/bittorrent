import sys, math, time, threading
import torrent, peer, downloader

tor = torrent.Torrent(sys.argv[1])
downloader = downloader.Downloader(tor)
tracker = tor.generate_tracker()
threads = []
cur_time = time.time()


def generate_peers():
    global threads, tracker
    peers = tracker.get_peers()
    for p in peers:
        peer_obj = peer.Peer(tor, downloader, p)
        t = threading.Thread(group=None,
                             target=peer_obj.download, name=None)
        threads.append(t)
        t.start()

generate_peers()
        
while not downloader.finished:
    threads = [t for t in threads if t.isAlive()]
    if time.time() - cur_time >= 60:
        print "wipe wip"
        downloader.clear_wip_pieces()
        cur_time = time.time()
    if len(threads) < 10:
        #print(len(threads))
        generate_peers()


    

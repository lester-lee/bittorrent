import sys
import math
import time
import threading
import torrent
import peer
import downloader

### SETUP ###
try:
    print "Reading torrent file..."
    #file_path = sys.argv[1]
    file_path = "ubuntu-600mb.torrent"
    tor = torrent.Torrent(file_path)
    #limit = int(sys.argv[2])
    limit = 0
    print "Creating the download session for this file..."
    downloader = downloader.Downloader(tor)
    print "Connecting to the tracker..."
    tracker = tor.generate_tracker()
    print "Peers found! Download starting."
except:
    print "Unable to download this torrent!"


### DOWNLOADING PIECES ###
threads = []
peers = set()
cur_time = time.time()

def create_thread(pr):
    '''
    create_thread will create a thread for the given peer @pr
    '''
    global threads
    threads.clear()
    t = threading.Thread(group=None,
                         target=pr.download, name=None)
    threads.append(t)
    t.start()

def generate_peers():
    '''
    generate_peers will ask the tracker for a list of peers
    and then create a thread for each peer.
    If specified, t will only create @limit number of threads.
    '''
    global peers, tracker, tor
    peers.update(tracker.get_peers())
    for p in peers:
        peer_obj = peer.Peer(tor, downloader, p, verbose=False)
        if limit and len(threads) < limit:


generate_peers(limit=lim)
max_num_peers = len(threads)

while not downloader.finished:
    threads = [t for t in threads if t.isAlive()]
    if time.time() - cur_time >= 60:
        downloader.clear_wip_pieces()
        cur_time = time.time()
    if len(threads) < (max_num_peers / 3):
        print "renewing peers"
        generate_peers()

import sys, math, time, threading
import torrent, peer, downloader

### SETUP ###
try:
    print "Reading torrent file..."
    file_path = sys.argv[1]
    tor = torrent.Torrent(file_path)
    limit = int(sys.argv[2])
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
    global threads, peers
    del threads[:]
    peers.update(tracker.get_peers())
    for p in peers:
        peer_obj = peer.Peer(tor, downloader, p, verbose=False)
        if limit and len(threads) < limit:
            create_thread(peer_obj)
        else:
            create_thread(peer_obj)


generate_peers()
max_num_peers = len(threads)

while not downloader.finished:
    threads = [t for t in threads if t.isAlive()]
    if time.time() - cur_time >= 60:
        downloader.clear_wip_pieces()
        cur_time = time.time()
    if len(threads) < (max_num_peers / 10):
        print "Requesting more peers"
        generate_peers()

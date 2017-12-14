import requests
import bencode

class Tracker:
    def __init__(self, torrent):
        self.urls = self.generate_urls(torrent, 6881, 6890)

    def generate_urls(self, tor, start_port, end_port):
        urls = []
        for port in range(start_port, end_port):
            url = "{}?info_hash={}&peer_id={}&port={}&uploaded={}&downloaded={}&left={}&compact={}&event={}".format(
                tor.announcer, tor.info_hash[1], tor.peer_id,
                port, 100000, 0, tor.info['length'], 1, "started")
            urls.append(url)
        return urls

    def get_peers(self):
        for url in self.urls:
            tracker = requests.get(url)
            if tracker.status_code == 200:
                break
        tracker_response = bencode.bdecode(tracker.text)
        peers = tracker_response['peers']
        peers = [peers[i:i+6] for i in range(0, len(peers), 6)]
        peers = [(x[:4], x[-2:]) for x in peers]
        return [self.parse_peer(p) for p in peers]

    def parse_peer(self, peer):
        ip = [str(ord(x)) for x in peer[0]]
        ip = ".".join(ip)
        port = [ord(x) for x in peer[1]]
        port = sum([port[-i+1]*256**i for i in range(len(port))])
        return (ip, port)

import random, string
import bencode
import hashlib, urllib
import tracker

class Torrent:
    def __init__(self, path):
        metadata = self.read_torrent(path)
        self.metadata = metadata
        self.announcer = metadata['announce']
        self.info = metadata['info']
        self.info_hash = self.get_info_hash()
        self.peer_id = self.generate_peer_id()
        
    def read_torrent(self, path):
        with open(path, 'rb') as f:
            return bencode.bdecode(f.read())

    def get_info_hash(self):
        info_hash20 = hashlib.sha1(bencode.bencode(self.info)).digest()
        info_hash = urllib.quote_plus(info_hash20)
        return (info_hash20, info_hash)

    def generate_peer_id(self):
        randstring = "".join(
            [random.choice(string.digits) for _ in range(12)])
        return "-ZZ0001-" + randstring

    def generate_tracker(self):
        return tracker.Tracker(self)
    
            

import random, string
import bencode
import hashlib, urllib
import tracker

class Torrent:
    '''
    Torrent is responsible for reading and decoding the
    .torrent file, and parsing out the relevant information.
    It also keeps track of the piece hashes.
    '''
    
    def __init__(self, path):
        metadata = self.read_torrent(path)
        self.metadata = metadata
        self.announcer = metadata['announce']
        self.info = metadata['info']
        self.name = metadata['info']['name']
        self.pieces = self.get_pieces(metadata['info']['pieces'])
        self.piece_length = metadata['info']['piece length']
        self.length = metadata['info']['length']
        self.info_hash = self.get_info_hash()
        self.peer_id = self.generate_peer_id()

    def read_torrent(self, path):
        with open(path, 'rb') as f:
            return bencode.bdecode(f.read())

    def get_info_hash(self):
        info_hash20 = hashlib.sha1(bencode.bencode(self.info)).digest()
        info_hash = urllib.quote_plus(info_hash20)
        return (info_hash20, info_hash)

    def get_pieces(self, piece_string):
        return [piece_string[i:i+20]
                for i in range(0,len(piece_string),20)]

    def get_piece_hash(self, index):
        return self.pieces[index]

    def generate_peer_id(self):
        return "".join([random.choice(string.digits) for _ in range(20)])

    def generate_tracker(self):
        return tracker.Tracker(self)

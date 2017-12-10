import math, hashlib
REQUEST_SIZE = 2**14

class Piece:
    def __init__(self, index, blocks):
        self.index = index
        self.blocks = blocks
        self.block_tracker = [0] * len(blocks)
        self.finished = False

    def reset(self):
        self.finished = False
        for b in self.blocks:
            b.data = None

    def save_block(self, start, data):
        for b_idx, block in enumerate(self.blocks):
            if block.start == start:
                block.data = data
                self.block_tracker[b_idx] = 1
        self.finished = self.block_tracker == [1] * len(self.blocks)
        
    def get_data(self):
        return b''.join([b.data for b in self.blocks])

class Block:
    def __init__(self, piece, start, length):
        self.piece = piece
        self.start = start
        self.length = length
        self.data = None

    def set_data(self, data):
        self.data = data

    def __repr__(self):
        return "Block: {} {} {} {}".format(
            self.piece, self.start, self.length, self.data)
    
class Downloader:
    def __init__(self, torrent):
        self.torrent = torrent
        self.pieces = self.generate_pieces()
        self.downloading_pieces = {}
        self.finished_pieces = {}
        self.final_data = [b''] * len(self.pieces)

    def generate_pieces(self):
        pieces = []
        blocks_per_piece = int(math.ceil(self.torrent.piece_length / REQUEST_SIZE))
        for p_idx in range(len(self.torrent.pieces)):
            blocks = []
            for b_idx in range(blocks_per_piece-1):
                blocks.append(Block(p_idx, REQUEST_SIZE * b_idx, REQUEST_SIZE))
            last_block_length = self.torrent.piece_length % REQUEST_SIZE
            blocks.append(Block(p_idx, self.torrent.piece_length - last_block_length,
                                last_block_length))
            pieces.append(Piece(p_idx, blocks))
        return pieces

    def get_next_piece(self):
        for piece in self.pieces:
            is_downloading = piece.index in self.downloading_pieces
            is_finished = piece.index in self.finished_pieces
            if is_downloading or is_finished:
                continue
            self.downloading_pieces[piece.index] = piece
            return piece

    def receive_block(self, piece_idx, start, data):
        piece = self.pieces[piece_idx]
        piece.save_block(start, data)
        if not piece.finished:
            return
        data = piece.get_data()
        check_hash = hashlib.sha1(data).digest()
        if check_hash != self.torrent.get_piece_hash(piece_idx):
            print 'bad piece hash'
            piece.reset()
            del self.downloading_pieces[piece_idx]
            return
        self.finished_pieces[piece_idx] = piece
        self.final_data[piece_idx] = piece.get_data()
        if len(self.finished_pieces) == len(self.pieces):
            self.write_to_file()

    def write_to_file(self):
        with open(self.torrent.name, 'wb') as f:
            f.write(b''.join(self.final_data)) 
        
                
        



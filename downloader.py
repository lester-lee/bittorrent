import math, hashlib
REQUEST_SIZE = 2**14

class Piece:
    '''
    A Piece represents a piece of the torrent file;
    It keeps a list of the blocks that must be downloaded.
    '''
    def __init__(self, index, blocks):
        self.index = index
        self.blocks = blocks
        self.finished_blocks = 0
        self.finished = False

    def reset(self):
        self.finished = False
        for b in self.blocks:
            b.data = None

    def save_block(self, start, data):
        for b_idx, block in enumerate(self.blocks):
            if block.start == start:
                block.data = data
                self.finished_blocks += 1
        self.finished = self.finished_blocks == len(self.blocks)

    def get_data(self):
        return b''.join([b.data for b in self.blocks])

    def __repr__(self):
        return "Piece {}: {}/{}".format(self.index, self.finished_blocks, len(self.blocks))

class Block:
    '''
    A Block represents a portion of a Piece, since a peer
    cannot send an entire Piece at once.
    '''
    def __init__(self, piece, start, length):
        self.piece = piece
        self.start = start
        self.length = length
        self.data = None

    def __repr__(self):
        return "Block: {} {} {} {}".format(
            self.piece, self.start, self.length, self.start)

class Downloader:
    '''
    Downloader represents the download session for one torrent file.
    It keeps track of all the pieces of the file, and is responsible
    for passing Block data to the appropriate Piece. Once all of the
    Pieces have the data for all of their Blocks, Downloader will write
    the file to disk.
    '''

    def __init__(self, torrent):
        self.torrent = torrent
        self.pieces = self.generate_pieces()
        self.num_pieces = len(self.pieces)
        self.downloading_pieces = {}
        self.finished_pieces = {}
        self.final_data = [b''] * len(self.pieces)
        self.finished = False

    def generate_pieces(self):
        '''
        generate_pieces will initialize a list of Pieces
        and their Blocks; no data is stored.
        '''
        pieces = []
        blocks_per_piece = int(math.ceil(self.torrent.piece_length / REQUEST_SIZE))
        for p_idx in range(len(self.torrent.pieces)):
            blocks = []
            for b_idx in range(blocks_per_piece):
                is_last = (blocks_per_piece - 1) == b_idx
                block_length = (self.torrent.piece_length % REQUEST_SIZE) or REQUEST_SIZE if is_last else REQUEST_SIZE
                blocks.append(Block(p_idx, block_length * b_idx, block_length))
            pieces.append(Piece(p_idx, blocks))
        return pieces

    def get_next_piece(self):
        '''
        get_next_piece will return the first available piece
        for a Peer to download.
        '''
        for piece in self.pieces:
            is_downloading = piece.index in self.downloading_pieces
            is_finished = piece.index in self.finished_pieces
            if is_downloading or is_finished:
                continue
            self.downloading_pieces[piece.index] = piece
            return piece

    def clear_wip_pieces(self):
        self.downloading_pieces.clear()

    def reset_piece(self, piece):
        piece.reset()
        if piece.index in self.downloading_pieces:
            del self.downloading_pieces[piece.index]

    def check_hash(self, piece_idx, piece):
        good_hash = self.torrent.get_piece_hash(piece_idx)
        data = piece.get_data()
        check_hash = hashlib.sha1(data).digest()
        return check_hash == good_hash

    def receive_block(self, piece_idx, start, data):
        '''
        receive_block is called by a Peer; it will pass
        the appropriate Block data to the corresponding Piece.
        If the Piece is finished, it will check the hash.
        If that was the final block to be downloaded, then
        all of the stored data will be written to disk.
        '''
        piece = self.pieces[piece_idx]
        piece.save_block(start, data)
        if not piece.finished: return
        if piece_idx in self.finished_pieces: return

        #print "Checking hash for piece {}".format(piece_idx)
        if not self.check_hash(piece_idx, piece):
            #print 'Bad hash for piece {}".format(piece_idx)
            self.reset_piece(piece)
            return

        self.finished_pieces[piece_idx] = piece
        print "Piece {}/{} is finished downloading!".format(piece_idx, self.num_pieces)
        self.final_data[piece_idx] = piece.get_data()
        print len(self.finished_pieces), self.num_pieces

        ### ALL PIECES HAVE BEEN DOWNLOADED ###
        if len(self.finished_pieces) >= self.num_pieces / 5:
            print "File is finished downloading!"
            self.finished = True
            #self.write_to_file()
            exit()

    def write_to_file(self):
        with open(self.torrent.name, 'wb') as f:
            f.write(b''.join(self.final_data))

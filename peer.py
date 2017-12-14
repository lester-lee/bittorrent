import socket, struct, copy


NOT_INTERESTED = struct.pack(">IB", 0001, 3)
INTERESTED = struct.pack(">IB", 0001, 2)
UNCHOKE = struct.pack(">IB", 0001, 1)
CHOKE = struct.pack(">IB", 0001, 0)
BUFFER_SIZE = 2**14   

class Peer:
    def __init__(self, torrent, downloader, info, verbose=False):
        self.ip_port = info
        self.torrent = torrent
        self.downloader = downloader
        self.handshake = self.generate_handshake()
        self.blocks = None 
        self.piece = None
        self.verbose = verbose

    def generate_handshake(self):
        return "".join([
            chr(19), "BitTorrent protocol", chr(0)*8,
            self.torrent.info_hash[0], self.torrent.peer_id])

    def check_handshake(self, socket):
        socket.send(self.handshake)
        peer_handshake = socket.recv(68)
        return self.torrent.info_hash[0] == peer_handshake[28:48]

    def send_interested(self, socket):
        if self.verbose: print "-> interested"
        socket.send(INTERESTED)

    def get_next_block(self):
        if self.downloader.finished: return None
        if (not self.piece) or (self.piece.finished) or len(self.blocks) == 0:
            self.piece = self.downloader.get_next_piece()
            self.blocks = copy.deepcopy(self.piece.blocks)
        return self.blocks.pop()

    def send_request(self, socket):
        block = self.get_next_block()
        if not block: return False
        if self.verbose: print "-> request {}:{}".format(block.piece, block.start)
        REQUEST = struct.pack('>IbIII', 13, 6, block.piece, block.start, block.length)
        socket.send(REQUEST)
        return True
        
    def download(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect(self.ip_port)
            if not self.check_handshake(s):
                #print "bad info hash"
                return
            self.send_interested(s)
            self.receive_messages(s)
            s.close()
        except:
            if self.piece: self.downloader.reset_piece(self.piece)
        
    def receive_messages(self, socket, verbose=False):
        buf = b''
        v = self.verbose
        while True:
        #for _ in range(10):
            #print "start of new loop"
            resp = socket.recv(BUFFER_SIZE)
            buf += resp
            while True:
                if len(buf) < 5: #not enough info to parse
                    break
                length = struct.unpack(">I", buf[:4])[0]

                if len(buf) < length: #payload not long enough
                    break

                def get_payload(buf):
                    return buf[:4+length]
                def read_buffer(buf):
                    return buf[4+length:]

                if length == 0:
                    if v: print "<- keep alive"
                    buf = read_buffer(buf)
                    raise Exception("messages not sending")

                mid = struct.unpack(">B", buf[4:5])[0]
                #print "message id:{}".format(mid)

                if mid == 0:
                    if v: print "<- choke"
                    buf = read_buffer(buf)
                    raise Exception("peer choked")
                elif mid == 1:
                    if v: print "<- unchoke"
                    buf = read_buffer(buf)
                elif mid == 2:
                    if v: print "<- interested"
                    buf = read_buffer(buf)
                elif mid == 3:
                    if v: print "<- not interested"
                    buf = read_buffer(buf)
                elif mid == 4:
                    if v: print "<- have"
                    buf = buf[5:] #have has fixed message length
                    buf = read_buffer(buf)
                elif mid == 5:
                    if v: print "<- bitfield"
                    bitfield = buf[5:5+length-1]
                    if v: print "Bitfield: {}".format(struct.unpack("B"*len(bitfield), bitfield))
                    buf = read_buffer(buf)
                elif mid == 6:
                    if v: print "<- request"
                    buf = read_buffer(buf)
                elif mid == 7:
                    payload = get_payload(buf)
                    buf = read_buffer(buf)
                    l = struct.unpack(">I",payload[:4])[0]
                    payload = struct.unpack(
                        ">IbII" + str(l-9) + "s",
                        payload[:length+4])
                    piece_idx, start, data = payload[2], payload[3], payload[4]
                    if v: print "<- piece {}".format(piece_idx)
                    self.downloader.receive_block(piece_idx, start, data)
                else:
                    print "unknown message id:{}".format(mid)
                    payload = get_payload(buf)
                    buf = read_buffer(buf)
                    if v: print "payload: {}".format(struct.unpack("B"*len(payload), payload))
                    return
                if not self.send_request(socket): return

import socket, struct


NOT_INTERESTED = struct.pack(">IB", 0001, 3)
INTERESTED = struct.pack(">IB", 0001, 2)
UNCHOKE = struct.pack(">IB", 0001, 1)
CHOKE = struct.pack(">IB", 0001, 0)
BUFFER_SIZE = 2**14   

class Peer:
    def __init__(self, torrent, info):
        self.ip_port = info
        self.torrent = torrent
        self.handshake = self.generate_handshake()

    def generate_handshake(self):
        return "".join([
            chr(19), "BitTorrent protocol", chr(0)*8,
            self.torrent.info_hash[0], self.torrent.peer_id])

    def check_handshake(self, socket):
        socket.send(self.handshake)
        peer_handshake = socket.recv(68)
        return self.torrent.info_hash[0] == peer_handshake[28:48]

    def send_interested(self, socket):
        print "-> interested"
        socket.send(INTERESTED)

    def send_request(self, socket):
        print "-> request"
        REQUEST = struct.pack(">IBBBI", 0013, 6, 0, 0, 2**14)
        socket.send(REQUEST)
        
    def download(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.ip_port)
        if not self.check_handshake(s):
            print "bad info hash"
            return
        self.send_interested(s)
        self.receive_messages(s)
        
    def receive_messages(self, socket):
        buf = b''
        while True:
            print "start of new loop"
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
                    print "<- keep alive"
                    buf = read_buffer(buf)

                mid = struct.unpack(">B", buf[4:5])[0]
                #print "message id:{}".format(mid)

                if mid == 0:
                    print "<- choke"
                    buf = read_buffer(buf)
                elif mid == 1:
                    print "<- unchoke"
                    buf = read_buffer(buf)
                elif mid == 2:
                    print "<- interested"
                    buf = read_buffer(buf)
                elif mid == 3:
                    print "<- not interested"
                    buf = read_buffer(buf)
                elif mid == 4:
                    print "<- have"
                    buf = buf[5:] #have has fixed message length
                    buf = read_buffer(buf)
                elif mid == 5:
                    print "<- bitfield"
                    bitfield = buf[5:5+length-1]
                    print "Bitfield: {}".format(struct.unpack("B"*len(bitfield), bitfield))
                    buf = read_buffer(buf)
                elif mid == 6:
                    print "<- request"
                    buf = read_buffer(buf)
                elif mid == 7:
                    print "<- piece"
                    #need to download the files!
                    #keep some indexed byte string
                    #once string is full, write string to file
                else:
                    print "unknown message id:{}".format(mid)
                self.send_request(socket)

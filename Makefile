all: unlimited 5 10 15 20 25 30
unlimited:
	time python bclient.py ubuntu-600mb.torrent 0
5:
	time python bclient.py ubuntu-600mb.torrent 5
10:
	time python bclient.py ubuntu-600mb.torrent 10
15:
	time python bclient.py ubuntu-600mb.torrent 15
20:
	time python bclient.py ubuntu-600mb.torrent 20
25:
	time python bclient.py ubuntu-600mb.torrent 25
30:
	time python bclient.py ubuntu-600mb.torrent 30

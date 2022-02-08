
import time
import socket
import msvcrt
from queue import Queue
from threading import Thread


HOST = "192.168.29.1"	# Microscope hard-wired IP address
SPORT = 20000			# Microscope command port
RPORT = 10900			# Receive port for JPEG frames
def jh_recv(out_q):
    frame_bytes = b''
    # Open command socket for sending
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # s.sendto(b"JHCMD\xd0\x00", (HOST, SPORT))
        # Send commands like naInit_Re() would do
        s.sendto(b"JHCMD\x10\x00", (HOST, SPORT))
        s.sendto(b"JHCMD\x20\x00", (HOST, SPORT))
        # Heartbeat command, starts the transmission of data from the scope
        s.sendto(b"JHCMD\xd0\x01", (HOST, SPORT))
        s.sendto(b"JHCMD\xd0\x01", (HOST, SPORT))

        # Open receive socket and bind to receive port
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as r:
            r.bind(("", RPORT))
            r.setblocking(0)
            first = True
            while True:
                try:
                    data = r.recv(1450)
                    if len(data) > 8:
                        # Header
                        framecount = data[0] + data[1]*256
                        packetcount = data[3]
                        #print("Frame %d, packet %d" % (framecount, packetcount))
                        # Data
                        if packetcount==0:
                            if not first:
                                out_q.put(frame_bytes)
                            else:
                                first = False
                            frame_bytes = b''
                            if framecount%10 == 0:
                                s.sendto(b"JHCMD\xd0\x01", (HOST, SPORT))
                        frame_bytes += data[8:]
                except socket.error:
                    time.sleep(0.01)
        # Stop data command, like in naStop()
        s.sendto(b"JHCMD\xd0\x02", (HOST, SPORT))
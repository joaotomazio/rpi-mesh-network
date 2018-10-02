import signal, sys
from threading import Thread
from threading import Lock
from time import sleep
from time import time
import shared.messages as messages
import shared.communication as communication
import shared.qrcode as qrcode
import shared.presentation as presentation
import shared.led as led

running = False
MYIP = None

thread1 = None
thread2 = None
thread3 = None
thread4 = None
thread5 = None

rtt = None
reset_timer = 20
wait_timer = 5

table = []				# Routing table
neighbours = []			# Neighbours table
tableLock = Lock()
neighboursLock = Lock()

###########################################################
# Name:		beacons
# Args:		-
# Return:	-
# Desc:		Thread function. Used to send multicast beacons
#			periodically to other nodes.
###########################################################
def beacons():
	global MYIP
	global running
	global table
	global tableLock
	count = 0

	while running:
		tableLock.acquire()
		try:
			messages.sendBeacons(MYIP, table)
		finally:
			tableLock.release()
		sleep(1)

##########################################################
# Name:		camera
# Args:		-
# Return:	-
# Desc:		Thread function. Used to send decoded QR code
#			messages to the server throughout other nodes.
##########################################################
def camera():
	global running
	global table
	global tableLock
	global rtt

	while running:
		img_str = qrcode.decode()
		if img_str is not None:
			tableLock.acquire()
			try:
				messages.sendDecoded(MYIP, table, img_str)
				rtt = time()
			finally:
				tableLock.release()
		sleep(2)

##########################################################
# Name:		waiting_msgs
# Args:		-
# Return:	-
# Desc:		Thread function. Used to receive all types of
#			messages or relay messages to other nodes.
#			Type 1 - Beacon
#			Type 2 - Authorization
#			Type 3 - Gate Control
##########################################################
def waiting_msgs():
	global running
	global MYIP
	global tableLock
	global table
	global rtt
	global neighbours
	global wait_timer
	
	while running:

		msg = communication.receive()
		if msg is None:
			continue
		if msg['from'][0] == MYIP:
			continue	

		led.blink("YELLOW_PIN")

		tableLock.acquire()
		neighboursLock.acquire()
		try:
			if msg['type'] == 1:
				table = messages.receiveBeacon(table, msg)
				neighbours = messages.updateNeighbours(neighbours, msg, table)
			elif msg['type'] == 4:
				table = [{'to': MYIP, 'hops': 0, 'via': MYIP}]
				sleep(wait_timer)
			elif msg['to'] != MYIP:
				messages.sendRelay(MYIP, table, msg)
			elif msg['type'] == 2:
				qrcode.checkAuth(MYIP, table, msg['from'][0], msg['content'])
			elif msg['type'] == 3:
				rtt = time() - rtt
				qrcode.gateControl(msg['content'])
		finally:
			tableLock.release()
			neighboursLock.release()

##########################################################
# Name:		visual
# Args:		-
# Return:	-
# Desc:		Thread function. Used to print relevant data
#			in the terminal shell.
##########################################################
def visual():
	global running
	global MYIP

	while running:
		presentation.print_info(MYIP, table, rtt, qrcode.allowed, qrcode.inpark)
		sleep(0.5)

##########################################################
# Name:		check_neighbours
# Args:		-
# Return:	-
# Desc:		Checks if the timer associated with each
#			neighbour node has timed out, meaning that
#			this node has failed.
##########################################################			
def check_neighbours():
	global neighbours
	global MYIP
	global table
	global running

	while running:
		for neighboursEntry in neighbours:
			if time() - neighboursEntry['timestamp'] > reset_timer:
				messages.sendCleanTables(MYIP, table)
				tableLock.acquire()
				neighboursLock.acquire()
				table = [{'to': MYIP, 'hops': 0, 'via': MYIP}]
				neighbours = []
				tableLock.release()
				neighboursLock.release()
		sleep(2)

##########################################################
# Name:		signal_handler
# Args:		-
# Return:	-
# Desc:		Signal handler associated with SIGINT signal.
#			Used to terminate the application by a
#			terminal user.
##########################################################			
def signal_handler(signal, frame):
	global running
	global thread1
	global thread2
	global thread3
	global thread4
	global thread5

	running = False

	communication.shutdown()
	led.shutdown()
	thread1.join()
	if sys.argv[1] == 2 or sys.argv[1] == 3:
		thread2.join()
	thread3.join()
	thread4.join()
	thread5.join()

##########################################################
# Name:		main
# Args:		sys.argv[1] - IP identifier of node
# Return:	-
# Desc:		Main function. Initializations, thread calls 
#			and shutdown procedures are done here.
#			thread1 - beacons()
#			thread2 - camera()
#			thread3 - waiting_msgs(
#			thread4 - visual()
##########################################################
if __name__ == "__main__":

	# Running in Pinto's Win10 inserts "\r\r" ???
	sys.argv[1] = sys.argv[1].replace("\r","")
	# Running in Pinto's Win10 inserts "\r\r" ???
	
	MYIP = 'fc01::' + sys.argv[1]
	table.append({'to': MYIP, 'hops': 0, 'via': MYIP})

	communication.setup()
	led.init()
	running = True

	thread1 = Thread(target=beacons, args=())
	thread1.start()

	if sys.argv[1] == '2' or sys.argv[1] == '3':
		qrcode.init()
		thread2 = Thread(target=camera, args=())
		thread2.start()
		
	thread3 = Thread(target=waiting_msgs, args=())
	thread3.start()

	thread4 = Thread(target=visual, args=())
	thread4.start()

	thread5 = Thread(target=check_neighbours, args=())
	thread5.start()

	signal.signal(signal.SIGINT, signal_handler)
	signal.pause()

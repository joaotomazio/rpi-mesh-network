import random, string, time
import shared.communication as communication
import shared.led as led

##########################################################
# Name:     sendBeacons
# Args:     -
# Return:   -
# Desc:     Prepare beacon message to be sent (type 1).
##########################################################
def sendBeacons(MYIP, table):
	communication.send({
		'id': randomString(),
		'type': 1,
		'to': 'all',
		'from': [MYIP],
		'content': table,
		'timestamp': time.time(),
	}, table)

##########################################################
# Name:     sendDecoded
# Args:     -
# Return:   -
# Desc:     Prepare QR code decoded message to be sent
#			(type 2).
##########################################################
def sendDecoded(MYIP, table, string):
	led.on('GREEN_PIN')
	led.on('RED_PIN')
	communication.send({
		'id': randomString(),
		'type': 2,
		'to': 'fc01::4',
		'from': [MYIP],
		'content': string,
		'timestamp': time.time(),
	}, table)

##########################################################
# Name:     sendAction
# Args:     -
# Return:   -
# Desc:     Prepares an action to a node to handle the
#			gate control to be sent (type 3).
##########################################################
def sendAction(MYIP, table, gate, control):
	communication.send({
		'id': randomString(),
		'type': 3,
		'to': gate,
		'from': [MYIP],
		'content': control,
		'timestamp': time.time(),
	}, table)

##########################################################
# Name:     sendCleanTables
# Args:     -
# Return:   -
# Desc:     Prepares a message to the neighbours to reset
#			their routing tables (type 4).
##########################################################
def sendCleanTables(MYIP, table):
	led.on('YELLOW_PIN')
	communication.send({
		'id': randomString(),
		'type': 4,
		'to': 'all',
		'from': [MYIP],
		'content': 'clear tables',
		'timestamp': time.time(),
	}, table)

##########################################################
# Name:     receiveBeacon
# Args:     -
# Return:   -
# Desc:     Receives beacon message and updates routing
#			if a better or new route is found to a node.
##########################################################
def receiveBeacon(table, msg):
	for msgEntry in msg['content']:
		found = False
		for tableEntry in table:
			if msgEntry['to'] == tableEntry['to']:
				found = True
				if msgEntry['hops'] + 1 < tableEntry['hops']:
					tableEntry['hops'] = msgEntry['hops'] + 1
					tableEntry['via'] = msg['from'][0]
		if not found:
			table.append({'to': msgEntry['to'], 'hops': msgEntry['hops'] + 1, 'via': msg['from'][0]})
	return table

##########################################################
# Name:     updateNeighbours
# Args:     -
# Return:   -
# Desc:     Checks if a new neighbour needs to be added to
#			the neighbours list or updates the timer
#			associated with an existent neighbour
##########################################################
def updateNeighbours(neighbours, msg, table):
	for tableEntry in table:
		found = False
		if tableEntry['hops'] == 1:
			for neighboursEntry in neighbours:
				if msg['from'][0] == neighboursEntry['via']:
					found = True
					neighboursEntry['timestamp'] = time.time()
			if not found:
				neighbours.append({'via': msg['from'][0], 'timestamp': time.time()})
	return neighbours

##########################################################
# Name:     sendRelay
# Args:     -
# Return:   -
# Desc:     Relays a received message to another node.
##########################################################
def sendRelay(MYIP, table, msg):
	msg['from'].append(MYIP)
	communication.send(msg, table)

##########################################################
# Name:     randomString
# Args:     -
# Return:   -
# Desc:     Random string generator for message ID.
##########################################################
def randomString():
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(16))
import picamera
import picamera.array
import zbar

from shared.messages import sendAction
import shared.presentation as presentation
import shared.led as led

camera = None
last = None
allowed = ['Zio', 'Pinto', 'Nuno'] 	# Allowed users
inpark = []											# In-park users

ENTRANCE_GATE = "fc01::2"							# IP of the entrance gate
EXIT_GATE = "fc01::3"								# IP of the exit gate

##########################################################
# Name:     init
# Args:     -
# Return:   -
# Desc:     Pi camera initialization.
##########################################################
def init():
	global camera
	camera = picamera.PiCamera()
	camera.resolution = (416, 400)

##########################################################
# Name:     decode
# Args:     -
# Return:   text - if a str was successfully decoded.
#			None - if no str was decoded.
# Desc:     QR code decoding with Pi camera.
##########################################################
def decode():
	global camera
	global last
	stream = picamera.array.PiYUVArray(camera)
	camera.capture(stream,format='yuv')
	scanner = zbar.ImageScanner()
	scanner.parse_config('enable')
	image = zbar.Image(416, 400, 'Y800', stream.array[..., 0].tostring())
	result = scanner.scan(image)
	if result == 1:
		for symbol in image:
			pass
		del(image)
		text = symbol.data.encode(u'utf-8')
		if text != last:
			last = text
			return text
		else:
			return None
	else:
		last = None
		return None

##########################################################
# Name:     commute
# Args:     info - Relevant information to be sent
#			(see checkAuth() function)
#			user - user to be checked
# Return:   -
# Desc:     Checks for a successfull commute of a user
#			to enter or exit the park.
##########################################################
def commute(info, user):
	global allowed
	global inpark
	control = 0
	if info['gate'] == ENTRANCE_GATE:
		if user in allowed and user not in inpark:
			control = 1
			inpark.append(user)	
	elif info['gate'] == EXIT_GATE:
		if user in inpark:
			control = 1
			inpark.remove(user)
	sendAction(info['IP'], info['table'], info['gate'], control)

##########################################################
# Name:     newuser
# Args:     user - user to be added
# Return:   -
# Desc:     Inserts a new user to the allowed list.
##########################################################
def newuser(info, user):
	global allowed
	if user not in allowed:
		allowed.append(user)
		sendAction(info['IP'], info['table'], info['gate'], 1)
	else:
		sendAction(info['IP'], info['table'], info['gate'], 0)

##########################################################
# Name:     removeuser
# Args:     user - user to be removed
# Return:   -
# Desc:     Removes a user from the allowed list.
##########################################################
def removeuser(info, user):
	global allowed
	try:
		allowed.remove(user)
		sendAction(info['IP'], info['table'], info['gate'], 1)
	except Exception as e:
		sendAction(info['IP'], info['table'], info['gate'], 0)
	
functions = {'newuser': newuser, 'removeuser': removeuser}

##########################################################
# Name:     checkAuth
# Args:     MYIP - IP of this node
#			table - Routing table
#			gate - IP of final node (which has a gate)
#			content - QR code content
# Return:   -
# Desc:     Splits the QR code content and checks if a
#			command is issued or if it has only a user.
#			Calls the commands described above.
##########################################################
def checkAuth(MYIP, table, gate, content):
	info = {'IP':MYIP, 'table':table, 'gate':gate}
	try:
		args = content.split(" ")
		functions[args[0]](info, args[1])
	except Exception as e:
		commute(info, content)

##########################################################
# Name:     gateControl
# Args:     control
# Return:   -
# Desc:     Controls the gate opening and the advertises
#			an allowed entrance with two LEDs.
##########################################################
def gateControl(control):
	global allowed
	global inpark
	led.off('GREEN_PIN')
	led.off('RED_PIN')
	if control == 0:
		led.warn('RED_PIN')
	elif control == 1:
		led.warn('GREEN_PIN')
		led.gateopen()

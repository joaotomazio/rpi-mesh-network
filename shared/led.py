import RPi.GPIO as GPIO
from time import sleep

codes = {'YELLOW_PIN': 36, 'RED_PIN': 38, 'GREEN_PIN': 40, 'SERVO_PIN': 12}

pwm = None

##########################################################
# Name:		init
# Args:		-
# Return:	-
# Desc:		LED and servo PWM initialization.
##########################################################
def init():
	global pwm
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(codes['YELLOW_PIN'], GPIO.OUT)
	GPIO.setup(codes['GREEN_PIN'], GPIO.OUT)
	GPIO.setup(codes['RED_PIN'], GPIO.OUT)
	GPIO.setup(codes['SERVO_PIN'], GPIO.OUT)
	pwm = GPIO.PWM(codes['SERVO_PIN'], 100)
	pwm.start(5)

	GPIO.output(codes['GREEN_PIN'], GPIO.LOW)
	GPIO.output(codes['RED_PIN'], GPIO.LOW)
	GPIO.output(codes['YELLOW_PIN'], GPIO.LOW)

##########################################################
# Name:		blink
# Args:		colour - LED colour
# Return:	-
# Desc:		LED short blink.
##########################################################
def blink(colour):
	GPIO.output(codes[colour], GPIO.HIGH)
	sleep(0.01)
	GPIO.output(codes[colour], GPIO.LOW)

##########################################################
# Name:		warn
# Args:		colour - LED colour
# Return:	-
# Desc:		LED long blink.
##########################################################
def warn(colour):
	GPIO.output(codes[colour], GPIO.HIGH)
	sleep(2)
	GPIO.output(codes[colour], GPIO.LOW)

##########################################################
# Name:		on
# Args:		colour - LED colour
# Return:	-
# Desc:		LED turn on.
##########################################################
def on(colour):
	GPIO.output(codes[colour], GPIO.HIGH)	

##########################################################
# Name:		off
# Args:		colour - LED colour
# Return:	-
# Desc:		LED turn off.
##########################################################
def off(colour):
	GPIO.output(codes[colour], GPIO.LOW)	

##########################################################
# Name:		gateopen
# Args:		-
# Return:	-
# Desc:		Servo rotate to simulate gate open/close
##########################################################
def gateopen():
	global pwm
	pwm.ChangeDutyCycle(10)
	sleep(5)
	pwm.ChangeDutyCycle(5)

##########################################################
# Name:		shutdown
# Args:		-
# Return:	-
# Desc:		LED and servo PWM shutdown.
##########################################################
def shutdown():
	global pwm
	pwm.stop()
	GPIO.cleanup()

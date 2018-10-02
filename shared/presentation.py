import os
from time import sleep

##########################################################
# Name:		print_info
# Args:		table - Routing table
#			rtt - Round Trip Time of a message
#			allowed - Users allowed to enter the park
#			inpark - Users in the park
# Return:	-
# Desc:		Used to print relevant data in the terminal
#			shell.
##########################################################
def print_info(MYIP, table, rtt, allowed, inpark):
	os.system('clear')

	print MYIP
	print "Routing Table\n"
	print("{}\t\t{}\t\t{}".format('  To', '  Hops', '  Via'))
	for k in table:
		print("{}\t\t{}\t\t{}".format(k['to'], k['hops'], k['via']))
	print "\n"
	
	if rtt is not None:
		print "RTT: " + str(rtt)
	else:
		print "\n"

	if MYIP == "fc01::4":
		if allowed:
			print "Allowed users:"
			for user in allowed:
				print user
			print ""

		if inpark:
			print "Inpark users:"
			for user in inpark:
				print user
			print ""

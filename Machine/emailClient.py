"""_________________________________________________
Simple class for sending email sequential updates about current
State of the Daa aquisition system

Writtin by: Maxwell Seifert AKA: cytznx
___________________________________________________"""


# Import smtplib for the actual sending function
import smtplib
import time

# Import the email modules we'll need
from email.mime.text import MIMEText

class emailClient(object):
	"""docstring for emailClient"""

	def __init__(self, arg):
		pass

	def sendMsg(self, send_Address, the_Msg, my_Adress="DoNotRespond@pqmfg.com"):

		#Construct the Message
		msg = MIMEText(the_Msg)
		msg['Subject'] = 'I have a question!!!'
		msg['From'] = my_Adress
		msg['To'] = send_Address

		# Send the message via our own SMTP server, but don't include the
		# envelope header.
		s = smtplib.SMTP('192.168.20.230', 25)
		s.sendmail(my_Adress, [send_Address], msg.as_string())
		s.quit()


	def sendUpdate(self, Addrees):
		pass


y = emailClient("pfffffffff")
for x in range(10):
	y.sendMsg("maxs@pqmfg.com","hey Cyrus... Why is the sky blue? x"+str(x+1))
	time.sleep(1)
	print "Sent message", x+1
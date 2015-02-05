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

	def __init__(self, server_adr='192.168.20.230', smtp_port=25):
		
		self.server_adr=server_adr
		self.smtp_port=smtp_port

		self.cyrusEmail = "CyrusJ@pqmfg.com"
		self.andrewEmail = "andrewH@pqmfg.com"
		self.deanEmail = "deanw@pqmfg.com"

		self.bruceEmail = "brucem@pqmfg.com"
		self.vahidEmail = "vahidK@pqmfg.com"

	def sendMsg(self, send_Address, the_Msg, my_Adress="vahidK@pqmfg.com"):

		#Construct the Message
		msg = MIMEText(the_Msg)
		msg['Subject'] = 'A Quick Question'
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
y.sendMsg("brucem@pqmfg.com","Hey Bruce, \n\n Weve had some unexpecred expenditures from manufacturing. Its been decided that you are no longer required her at product quest. Jason will fill you in on the details \n\n Thanks, \n Vahid")

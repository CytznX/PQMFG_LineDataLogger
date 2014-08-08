from twilio.rest import TwilioRestClient

#My Twillio Numbe: (860) 785-2231

# Your Account Sid and Auth Token from twilio.com/user/account
def sendTxtMsg(message,
								account_sid = "ACe5c41ae6ff35260590f43b90081e40d9",
								auth_token = "884e3bf7dfc49708ad05013105532713"):

	client = TwilioRestClient(account_sid, auth_token)

	message = client.messages.create(body=message,
			to="+18608788325",     # Destination
			from_="+18607852231")  # Origin

	return message.sid

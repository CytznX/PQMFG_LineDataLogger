
class BCscanner():

	def __init__(self):
		self.messageholder = [[]]

	def add(self, keypress = ''):
		if not keypress == '13':
			if self.messageholder == []:
				self.messageholder.append([keypress])
			else:
				self.messageholder[0].append(keypress)
		else:
			self.messageholder[0].append(keypress)
			self.messageholder.insert(0,[])

		#print 'added: ', keypress

	def getAvalibleMessage(self):
		shitkey = False
		message = ''

		if not self.messageholder == [[]] and not self.messageholder==[]: 
			if self.messageholder[-1][-1] == 13:
				for letters in self.messageholder.pop():


					try:

						if shitkey and letters == 51:
							message += '#'
							shitkey = False
						elif letters == 45:
							message += '_'
							shitkey = False
						else:
							message += chr(letters)
							shitkey = False

						#print 'added :', letters,chr(letters)

					except ValueError:
						if letters == 304:
							shitkey = True

		return message.upper()[:-1]

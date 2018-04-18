import os 				# For env variables
import threading			# Enables use as module in slackbot
from time import sleep			# For sleep()
from datetime import datetime		# To get system time
from slackclient import SlackClient	# For Slack Client

Dante_Close_Hours = [1,9,17]

Dante_Open_Hours = [2,10,16]

sc = SlackClient(os.environ['TESTING_TOKEN']);

class danteUpdater (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		print ("Starting Dantes Updater")
		

	def start (token):
		while True:
			send = False
			longSleep = False
			curTime = datetime.now()
			if curTime.hour in Dante_Close_Hours:
				if curTime.minute == 40:
					message = "WARNING: Dante's Forest closes in 5 minutes"
					send = True
				elif curTime.minute == 45:
					message = "Dante's Forest is now closed"
					send = True
			
			if curTime.hour in Dante_Open_Hours:
				if curTime.minute == 1:
					message = "Dante's Forest is now open. Happy Hunting!"
					send = True
					longSleep = True
			if send:
				sc.api_call(
					"chat.postMessage",
					channel="#general",
					text=message
					)
			
			if longSleep:
				sleep(27000)
		
			sleep(60)


import os 				# For env variables
import threading			# Enables use as module in slackbot
from time import sleep			# For sleep()
from datetime import datetime		# To get system time
from slackclient import SlackClient	# For Slack Client
from InfraBot import InfraBot

Dante_Close_Hours = [1,9,17]

Dante_Open_Hours = [2,10,16]


''' Class that defines a danteUpdater Thread. This thread is responsible for updating the
    general channel 5 minutes before Dantes Forest Closes, when Dante's Forest closes, and
    when Dantes Forest opens again '''
class DantesUpdater:
    def __init__(self, token):
        self.__token = token
        self.__curThread = DantesUpdater_Thread(self.__token)

    def api_entry(self, message, channel, user):
        if message == "start":
            if not InfraBot.checkPermission(user, "admin"):
                InfraBot.sendEphemeral("Access Denied", channel, user)
                return "Access Denied"
            if self.__curThread.status():
                self.__curThread.stop()
                self.__curThread = DantesUpdater_Thread(self.__token)
                self.__curThread.start()
                InfraBot.sendEphemeral("Restarted Dantes Updater", channel, user)
            else:
                self.__curThread.start()
                InfraBot.sendEphemeral("Started Dantes Updater", channel, user)
            return "Started Dantes Updater"
        elif message == "stop":
            if not InfraBot.checkPermission(user, "admin"):
                InfraBot.sendEphemeral("Access Denied", channel, user)
                return "Access Denied"
            self.__curThread.stop()
            self.__curThread = DantesUpdater_Thread(self.__token)
            InfraBot.sendEphemeral("Stopped Dantes Manager", channel, user)
            return "Stopped Dantes Updater"
        elif message == "status":
            if self.__curThread.status():
                InfraBot.sendMessage("Status: Running", channel)
            else:
                InfraBot.sendMessage("Status: Stopped", channel)
        else:
            return "Command not found"

class DantesUpdater_Thread(threading.Thread):
    ''' Initializer for danteUpdater object
        Input:
            token: API token to commuicate with the slack team
        Output:
            danteUpdater object
    '''
    def __init__(self, token):
        threading.Thread.__init__(self)
        self.__sc = SlackClient(token)
        self.__lock = threading.Lock()
        self.__continue = False
        self.__send = False
        self.__longsleep = False

    ''' Function that starts the updater in its own thread, called by start() SHOULD NOT
        BE CALLED BY ITSELF
        Input:
            N/A
        Output:
            N/A
    '''
    def run(self):
        print ("Starting Dantes Updater")
        self.start_loop()

    ''' Main thread body, determines if a message needs to be sent, otherwise sleeps '''
    def start_loop (self):
        self.__continue = True
        while True:
            self.__longSleep = False
            curTime = datetime.now()
            if curTime.hour in Dante_Close_Hours:
                if curTime.minute == 40:
                    self.__message = "WARNING: Dante's Forest closes in 5 minutes"
                    self.__send = True
                elif curTime.minute == 45:
                    self.__message = "Dante's Forest is now closed"
                    self.__send = True

            if curTime.hour in Dante_Open_Hours:
                if curTime.minute == 1:
                    self.__message = "Dante's Forest is now open. Happy Hunting!"
                    self.__send = True
                    self.__longSleep = True

            if self.__send:
                InfraBot.sendMessage(self.__message, "#general")
                self.__send = False

            if self.__longSleep:
                sleep(27000)

            sleep(60)

            self.__lock.acquire()
            if not self.__continue:
                self.__lock.release()
                break
            else:
                self.__lock.release()

    ''' Function to  stop the updater thread, may take up to 7.5 hours to exit (will return immediately) '''
    def stop (self):
        self.__lock.acquire()
        self.__continue = False
        self.__lock.release()

    ''' Function that indicates if the updater is running
        Input:
            N/A
        Output:
            A boolean indicating if the module is running
    '''
    def status (self):
        self.__lock.acquire()
        status = self.__continue
        self.__lock.release()
        return status


import os 				# For env variables
import threading			# Enables use as module in slackbot
from time import sleep			# For sleep()
from datetime import datetime		# To get system time
import InfraBot
from InfraModule import InfraModule

Dante_Close_Hours = [1,9,17]

Dante_Open_Hours = [2,10,18]

''' Class that defines a danteUpdater Thread. This thread is responsible for updating the
    general channel 5 minutes before Dantes Forest Closes, when Dante's Forest closes, and
    when Dantes Forest opens again '''
class Dantes_Updater(InfraModule):
    def __init__(self):
        super().__init__("dante", None)
        self.__curThread = DantesUpdater_Thread()
        self.__curThread.setDaemon(True)
        self.__curThread.start()

    def api_entry(self, message, channel, user, team_id):
        if message == "start":
            if not InfraBot.checkPermission(user, "admin", team_id):
                InfraBot.sendEphemeral("Access Denied", channel, user, team_id)
                return "Access Denied"

            self.__curThread.add_list(channel, team_id)
            InfraBot.sendEphemeral("Started Dantes Updater", channel, user, team_id)
            return "Started Dantes Updater"

        elif message == "stop":
            if not InfraBot.checkPermission(user, "admin", team_id):
                InfraBot.sendEphemeral("Access Denied", channel, user, team_id)
                return "Access Denied"

            self.__curThread.remove_list(channel, team_id)
            InfraBot.sendEphemeral("Stopped Dantes Manager", channel, user, team_id)
            return "Stopped Dantes Updater"

        elif message == "status":
            if self.__curThread.status():
                InfraBot.sendMessage("Status: Running", channel, team_id)
            else:
                InfraBot.sendMessage("Status: Stopped", channel, team_id)
        else:
            return "Command not found"

class DantesUpdater_Thread(threading.Thread):
    ''' Initializer for danteUpdater object
        Input:
            token: API token to commuicate with the slack team
        Output:
            danteUpdater object
    '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.__lock = threading.Lock()
        self.__continue = False
        self.__send = False
        self.__longsleep = False
        self.__listLock = threading.Lock()
        self.__updateList = []

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
                self.send_updates(self.__message)
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
        self.__listLock.acquire()
        if self.__updateList == []:
            status = True
        else:
            status = False
        self.__listLock.release()
        return status

    def add_list (self, newChannel, newTeam):
        self.__listLock.acquire()
        if not (newChannel, newTeam) in self.__updateList:
            self.__updateList.append((newChannel,newTeam))
            print("Dantes Updater: Added new channel to Update List")

        else:
            print("Dantes Updater: Channel already in Update List")

        self.__listLock.release()

    def remove_list (self, remChannel, remTeam):
        self.__listLock.acquire()
        if (remChannel, remTeam) in self.__updateList:
            self.__updateList.remove((remChannel, remTeam))
            print("Dantes Updater: Removed channel from Update List")

        else:
            print("Dantes Updater: Channel not in Update List")

        self.__listLock.release()

    def send_updates(self, message):
        for (sendChannel, sendTeam) in self.__updateList:
            InfraBot.sendMessage(message, sendChannel, sendTeam)


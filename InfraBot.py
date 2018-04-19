import os				# To access tokens
from DantesUpdater import danteUpdater	# To access DantesUpdator
from flask import Flask
from flask.ext.api import status

app = Flask(__name__)

@app.route("/")
def main():
	return "Welcome"

@app.route("/test")
def test():
	print("RECIEVED TEST!")
	return status.HTTP_200_OK

#dante = danteUpdater(os.environ['TESTING_TOKEN'])

#dante.start()

#input()

#dante.stop()
#print("Waiting for thread to stop")
#dante.join()


if __name__ == "__main__":
	app.run()

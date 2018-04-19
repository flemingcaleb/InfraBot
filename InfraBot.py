import os				# To access tokens
from DantesUpdater import danteUpdater	# To access DantesUpdator

dante = danteUpdater(os.environ['TESTING_TOKEN'])

dante.start()

input()

dante.stop()
print("Waiting for thread to stop")
dante.join()


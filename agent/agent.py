import requests
from time import sleep

timeToWait = 300 # Time to wait between callouts (in seconds)

while (True):
    # Get list of commands to run this callout
    URL = "https://slack.flemingcaleb.com:5000/api/agent/4/command/"
    r = requests.get(url=URL)

    if r.status_code == requests.codes.ok:
        # Process the list of requests
        print(r)
    elif r.status_code == requests.codes.not_found:
        # No list this time
        print("No list this time")
    else:
        #Handle Unintended Error
        print("ERROR")

    sleep(timeToWait)

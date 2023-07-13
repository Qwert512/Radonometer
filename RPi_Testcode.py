import requests, time, random
url = "https://goldfisch.tk/new/"
while True:
    try:
        rand_1 = random.randint(1,2)
        resp = requests.post(url+str(rand_1))
        print("Send value "+str(rand_1)+" with response: "+str(resp.content))
        delay = random.randint(5,30)
        time.sleep(delay)
    except:
        time.sleep(5)
        print("error")
        pass
import requests, time, random
url = "http://192.168.56.1:80/cpm/"
offset = 0
delay = 1
count = 0
while True:
    try:
        rand_2 = random.randint(5+offset,8+offset)
        if rand_2 < 0:
            rand_2 = 0
        rand_1 = random.randint(rand_2,13+offset)
        if rand_1 < 0:
            rand_1 = 0
        resp = requests.post(url+str(rand_1))
        print("Send value "+str(rand_1)+" with response: "+str(resp.content))
        time.sleep(delay)
        count += 1
        if count == 40:
            delay = 60
    except:
        time.sleep(5)
        print("error")
        pass
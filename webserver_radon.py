import time, math, statistics, os, json
from datetime import datetime
from typing import Dict
import numpy as np, uvicorn, random
import matplotlib.pyplot as plt
from fastapi_offline import FastAPIOffline
from fastapi import responses
from brokenaxes import brokenaxes
from cycler import cycler
from render import render
from process_data import plot


version = "0.1.8" 
app = FastAPIOffline(
    title="Radonometer 9000",
    version=version,
    description="Backend der Seminararbeit 'Radondetektor' von Qwert512"
    )
last_time = float()
times = []
values = []
mins = []
start_time_s = time.time()
start_time = datetime.now()
print("Start time: "+str(start_time_s)+" s")
default_json_data = {
    "data":{
        "start_time_s":start_time_s,
        "raw_minutes":{}
            }
}


data_file = "data.json"

if __name__ == "__main__":
    uvicorn.run("webserver_radon:app", host="127.0.0.1", port=8000)

@app.get("/")
def root():
    return{"version":version}

def update_data(data:str):
    global start_time
    if not os.path.exists(data_file):
        with open(data_file, "w") as file:
            file.write(json.dumps(default_json_data))
    if os.stat(data_file).st_size == 0:
        with open(data_file, "w") as file:
            file.write(json.dumps(default_json_data))
    
    with open(data_file, "r") as file:
        try:
            existing_data = json.load(file)
        except json.decoder.JSONDecodeError:
            existing_data = {}
    start_time = datetime.fromtimestamp(float(existing_data["data"]["start_time_s"]))
    time_elapsed = datetime.now() - start_time
    minutes_elapsed = math.ceil(time_elapsed.total_seconds() / 60)
    
    if True:
        #rohr 1:
        if "rohr_1" not in existing_data["data"]["raw_minutes"]:
            existing_data["data"]["raw_minutes"]["rohr_1"] = {}

        if str(minutes_elapsed-1) not in existing_data["data"]["raw_minutes"]["rohr_1"]:
            if str(minutes_elapsed-3) in existing_data["data"]["raw_minutes"]["rohr_1"] and\
                str(minutes_elapsed-2) not in existing_data["data"]["raw_minutes"]["rohr_1"]:
                    existing_data["data"]["raw_minutes"]["rohr_1"][str(minutes_elapsed-2)] = 0
                    existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed-2)] = 0

            if str(minutes_elapsed-2) in existing_data["data"]["raw_minutes"]["rohr_1"]:
                existing_data["data"]["raw_minutes"]["rohr_1"][str(minutes_elapsed-1)] = 0
                existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed-1)] = 0
            
        #fills small holes in the data if necessary. So for example if There is a value 
        #three minutes ago and in the current minute, it can be assumed, that the device 
        # was working for the two empty minutes, so they are filled with 0 CPM
            
        if str(minutes_elapsed) not in existing_data["data"]["raw_minutes"]["rohr_1"]:
            existing_data["data"]["raw_minutes"]["rohr_1"][str(minutes_elapsed)] = 0

        if data == "1":
            existing_data["data"]["raw_minutes"]["rohr_1"][str(minutes_elapsed)] += 1
        

        
        #rohr 2:

        if str(minutes_elapsed) not in existing_data["data"]["raw_minutes"]["rohr_2"]:
            existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed)] = 0

        if str(minutes_elapsed-1) not in existing_data["data"]["raw_minutes"]["rohr_2"]:
            print("min -1 = None")
            if str(minutes_elapsed-3) in existing_data["data"]["raw_minutes"]["rohr_2"] and\
                str(minutes_elapsed-2) not in existing_data["data"]["raw_minutes"]["rohr_2"]:
                    existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed-2)] = 0

            if str(minutes_elapsed-2) in existing_data["data"]["raw_minutes"]["rohr_2"]:
                existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed-1)] = 0
            
        #fills small holes in the data if necessary. So for example if There is a value 
        #three minutes ago and in the current minute, it can be assumed, that the device 
        # was working for the two empty minutes, so they are filled with 0 CPM

        if "rohr_2" not in existing_data["data"]["raw_minutes"]:
            existing_data["data"]["raw_minutes"]["rohr_2"] = {}    

        if data == "2":
            existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed)] += 1
    #little bit of data processing
        
    with open(data_file, "w") as file:
        json.dump(existing_data, file)
    
    print("Data saved successfully in minute "+str(minutes_elapsed)+".")

@app.post("/new/{data}")
async def add_new_data(data: str):
    print("Received data: "+str(data)+" at "+str(time.time()))
    update_data(data)
    return {"message": "Data received and saved."}

@app.get("/data")
async def get_data():
    with open(data_file,"r") as file:
        json_data = json.load(file)
    return json_data

@app.get("/visualize_data")
async def return_plot(time_window_mins:int,x_width:float=6,y_height:float=4,minimum_x_len:int=2,dark_mode:bool=False):
    start_time_ms = math.floor(time.time()*1000)
    with open("data.json","r") as file:
        data = json.load(file)["data"]
        file.close()
    await plot(json_data=data,x_width=x_width,y_height=y_height,x_axis_mins=time_window_mins,minimum_x_len=minimum_x_len,dark_mode=dark_mode,start_time_ms=start_time_ms)
    return responses.FileResponse("last_x_mins.png")
    

@app.get("/status")
async def status():
    rad_status = 0
    rad_status = random.randint(1,3)
    # try:
    #     avg = statistics.mean(mins)
    #     if avg <= 15:
    #         rad_status = 1
    #     if avg > 15 and avg <= 30:
    #         rad_status = 2
    #     if avg > 30:
    #         rad_status = 3
    # except:
    #     pass
    messages = ["just chillin","*slightly* concerning","you are die!"]
    message = messages[rad_status-1]

    return responses.JSONResponse(content={"status": str(rad_status),  "message":message},headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type", "Content-Type": "application/json"})



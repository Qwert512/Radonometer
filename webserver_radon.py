import time, math, statistics, os, json
from datetime import datetime
from typing import Dict
import numpy as np, uvicorn
import matplotlib.pyplot as plt
from fastapi import FastAPI, responses

app = FastAPI()
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

def update_data(data:str, time_format="%Y-%m-%d %H:%M:%S"):
    global start_time
    if not os.path.exists(data_file):
        with open(data_file, "w") as file:
            file.write(json.dumps(default_json_data))
    if os.stat(data_file).st_size == 0:
        with open(data_file, "w") as file:
            file.write(json.dumps(default_json_data))

    current_time = datetime.now().strftime(time_format)
    
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

async def update_plots():
    start_time = time.time()
    data = []
    len_mins = len(mins)
    start = len_mins-60
    for i in range (start,len_mins):
        try:
            data.append(mins[i])
        except:
            data.append(0)

    # Smooth the data
    window_size = min(10, len(data))  # Use a window size of 10 or the length of the data array, whichever is smaller
    smoothed_data = np.convolve(data, np.ones(window_size) / window_size, mode='same')

    # Generate the x-axis values
    minutes_x = np.arange(60)  # Fixed x-axis of 60 minutes

    # Plot the graph
    plt.figure(figsize=(16, 9), dpi=120)
    plt.plot(minutes_x, data, label="Geiger counter activity")
    plt.plot(minutes_x, smoothed_data, label="Smoothed geiger counter activity")
    plt.xlabel("Time (mins)")
    plt.ylabel("Activity (CPM)")
    plt.legend(loc='upper right')
    plt.title("Last 60 minutes of Data")
    plt.savefig("last_60_minutes.png")
    plt.clf()
    plt.close()
    end_time = time.time()
    time_difference = round(end_time-start_time,4)
    print("\nUpdated all plots in "+str(time_difference)+" seconds\n")
    print(mins)

@app.get("/last_hour")
async def get_picture():
    await update_plots()
    return responses.FileResponse("last_60_minutes.png")

@app.get("/status")
async def status():
    rad_status = 0
    try:
        avg = statistics.mean(mins)
        if avg <= 15:
            rad_status = 1
        if avg > 15 and avg <= 30:
            rad_status = 2
        if avg > 30:
            rad_status = 3
    except:
        pass
    print(mins)
    return {"status":str(rad_status)}
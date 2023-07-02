import time, math, statistics, os, json
from datetime import datetime
from typing import Dict
import numpy as np
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
    
    if "rohr_1" not in existing_data["data"]["raw_minutes"]:
        existing_data["data"]["raw_minutes"]["rohr_1"] = {}
        
    if "rohr_2" not in existing_data["data"]["raw_minutes"]:
        existing_data["data"]["raw_minutes"]["rohr_2"] = {}
    
    if str(minutes_elapsed) not in existing_data["data"]["raw_minutes"]["rohr_1"]:
        existing_data["data"]["raw_minutes"]["rohr_1"][str(minutes_elapsed)] = 0
    
    if str(minutes_elapsed) not in existing_data["data"]["raw_minutes"]["rohr_2"]:
        existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed)] = 0
        
    if data == "1":
        existing_data["data"]["raw_minutes"]["rohr_1"][str(minutes_elapsed)] += 1

    elif data == "2":
        existing_data["data"]["raw_minutes"]["rohr_2"][str(minutes_elapsed)] += 1
  
    
    with open(data_file, "w") as file:
        json.dump(existing_data, file)
    
    print("Data saved successfully in minute "+str(minutes_elapsed)+".")

@app.post("/new/{data}")
async def add_new_data(data: str):
    update_data(data)
    return {"message": "Data received and saved."}


@app.post("/cpm/{rohr}")
async def add_new_data(rohr: str):
    file_path = "data.json"
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write(default_json_data)
    if os.stat(file_path).st_size == 0:
        with open(file_path, "w") as file:
            file.write(default_json_data)
    
    timestamp = time.time()
    if times == []:
        delta_to_last = 0.0
        last_time = timestamp
    else:
        delta_to_last = last_time - timestamp
        last_time = timestamp
    for i in range(len(times)):
        val = times[i]
        val += delta_to_last
        times[i] = round(val,2)
    times.append(0)
    mins.append(int(data))
    #print(f"Received new data: {data} with delta time: {delta_to_last:.2f}")
    return {"message": "Data received"}


@app.get("/data")
async def get_data():
    return values,times,mins

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
    plt.savefig("last_60_minutes.jpg")
    plt.clf()
    plt.close()
    end_time = time.time()
    time_difference = round(end_time-start_time,4)
    print("\nUpdated all plots in "+str(time_difference)+" seconds\n")
    print(mins)

@app.get("/last_hour")
async def get_picture():
    await update_plots()
    return responses.FileResponse("last_60_minutes.jpg")

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
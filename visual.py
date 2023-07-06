import time, math, statistics, random
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

@app.post("/cpm/{data}")
async def add_new_data(data: str):
    global last_time, times, values
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
    return values,times

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
    return {"status": str(rad_status),  "message":message}


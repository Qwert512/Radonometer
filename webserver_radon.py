import time, math, statistics, os, json
from datetime import datetime
from typing import Dict
import numpy as np, uvicorn, random
import matplotlib.pyplot as plt
from fastapi import FastAPI, responses
from brokenaxes import brokenaxes

version = "0.1.5" 
app = FastAPI(
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

@app.get("/visualize_data")
async def return_plot(time_window_mins:int,x_width:float=6,y_height:float=4,minimum_x_len:int=2):
    with open("data.json","r") as file:
        data = json.load(file)["data"]
        file.close()
    await plot(json_data=data,x_width=x_width,y_height=y_height,x_axis_mins=time_window_mins,minimum_x_len=minimum_x_len)
    return responses.FileResponse("last_x_mins.png")

async def plot(json_data:dict,x_width:float,y_height:float,x_axis_mins:int,minimum_x_len:int=2):
    if x_axis_mins == 0:
        x_axis_mins = 2000000000
    start_time_ms = math.floor(time.time()*1000)
    if y_height < 1:
        y_height = 1
    if x_width < 1:
        x_width = 1
    #define some variables and fetch some basic data
    jumps_1 = ()
    jumps_2 = ()
    keys_1 = list(json_data["raw_minutes"]["rohr_1"].keys())
    last_key_1 = keys_1[len(keys_1)-1]
    first_key_1 = int(last_key_1) - x_axis_mins
    keys_2 = list(json_data["raw_minutes"]["rohr_2"].keys())
    last_key_2 = keys_2[len(keys_2)-1]
    first_key_2 = int(last_key_2) - x_axis_mins

    #processing for "Rohr_1"
    if True:
        if first_key_1 <= 0:
            first_key_1 = 0
            #check if it neccesary to remove values based on the provided time window
        else:
            for i in reversed(keys_1):
                i = int(i)
            #iterate through the time values in minutes
                if i < first_key_1:
                    json_data["raw_minutes"]["rohr_1"].pop(str(i))
                    keys_1.remove(str(i))
            #then pop all the values that do not fit in the specified time window

        previous_num = int(keys_1[0])
        offset = previous_num
        if int(keys_1[0])+1<int(keys_1[1]):
            offset -= int(keys_1[1]) - int(keys_1[0])
        for i in range(len(keys_1) - 1):
            if int(keys_1[i+1]) > int(keys_1[i]) + 1:
                #print("Minute "+str(keys_1[i])+" = minute "+str(int(keys_1[i])-offset)+" from start")
                old_tuple = jumps_1
                new_tuple = old_tuple + ((previous_num-offset, int(keys_1[i])-offset),)
                previous_num = int(keys_1[i+1])
                jumps_1 = new_tuple
        old_tuple = jumps_1
        jumps_1 = old_tuple + ((previous_num-offset, int(keys_1[i])-offset),)
        jumps_1 = [(a, b) for (a, b) in jumps_1 if abs(a - b) >= minimum_x_len]

        if int(keys_1[i]) == int(keys_1[i-1])+1:
            modified_tuple = [*jumps_1[-1][:-1], jumps_1[-1][-1] + 1]
            jumps_1 = tuple([list(t) if t != jumps_1[-1] else modified_tuple for t in jumps_1])

        #this is pretty complicated, just ignore it. It does some black magic and then the data is 
        #sorted, crisp, cleaned and stuffed into the right output format

    # ?processing for "Rohr_2"
    # !Commented out because a lot is being done on the rohr 1 part, and im too lazy to update dis
    # if True:

    #     if first_key_2 <= 0:
    #         first_key_2 = 0
    #         #see for the "rohr_1" code block
    #     else:
    #         for i in reversed(keys_2):
    #             i = int(i)

    #             if i < first_key_2:
    #                 json_data["raw_minutes"]["rohr_2"].pop(str(i))
    #                 keys_2.remove(str(i))


    #     previous_num = first_key_2
    #     for i in range(len(keys_2) - 1):
    #         if int(keys_2[i+1]) > int(keys_2[i]) + 1:
    #             old_tuple = jumps_2
    #             new_tuple = old_tuple + ((previous_num, int(keys_2[i])),)
    #             previous_num = int(keys_2[i+1])
    #             jumps_2 = new_tuple
    #     old_tuple = jumps_2
    #     jumps_2 = old_tuple + ((previous_num, int(keys_2[i])),)
    #     jumps_2 = [(a, b) for (a, b) in jumps_2 if abs(a - b) >= minimum_x_len]

    #     if int(keys_2[i]) == int(keys_2[i-1])+1:
    #         modified_tuple = [*jumps_2[-1][:-1], jumps_2[-1][-1] + 1]
    #         jumps_2 = tuple([list(t) if t != jumps_2[-1] else modified_tuple for t in jumps_2])

    # Create a figure and axes

    plt.figure(figsize=(x_width, y_height),dpi=120)
    ax = brokenaxes(xlims=jumps_1, hspace=0.05)

    # convert all  minute values from str to int and substract the start value from them, so the diagram starts at 0
    x_values = []
    for val in list(json_data["raw_minutes"]["rohr_1"].keys()):
        val = int(val)
        val -= offset
        x_values.append(val)
    window_size = min(10, len(list(json_data["raw_minutes"]["rohr_1"].values())))  # Use a window size of 10 or the length of the data array, whichever is smaller
    smoothed_data = np.convolve(list(json_data["raw_minutes"]["rohr_1"].values()), np.ones(window_size) / window_size, mode='same')
    #print("Values on x axis: "+str(x_values))
    #print("jumps: "+str(jumps_1))
    # Plot data on the broken axes
    
    ax.plot(x_values,
            list(json_data["raw_minutes"]["rohr_1"].values()), 'c-',label="Geiger counter activity")
    ax.plot(x_values,
            smoothed_data, 'r-', label="Smoothed Geiger counter activity")
    ax.legend(loc='upper right')
    if x_axis_mins == 2000000000:
        plt.title("All data")
    else:
        plt.title("Last "+str(x_axis_mins)+" minutes of data")
    ax.set_xlabel("Time (mins)")
    ax.set_ylabel("Activity (CPM)")

    # Save the plot
    plt.savefig("last_x_mins.png")
    plt.clf()
    plt.close()
    time_diff_ms = math.floor(time.time()*1000) - start_time_ms
    print("Successfully updated all plots in "+str(time_diff_ms)+"ms")
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

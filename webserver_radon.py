import time, math, statistics, os, json
from datetime import datetime
from typing import Dict
import numpy as np, uvicorn, random
import matplotlib.pyplot as plt
from fastapi_offline import FastAPIOffline
from fastapi import responses
from brokenaxes import brokenaxes#



version = "0.1.6" 
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
    # Plot data on the broken axes
        
    x_axis_values, unit, plot_title, div_val = await label_x_axis_and_title(x_values=x_values)
        
    ax.plot(x_axis_values,
            list(json_data["raw_minutes"]["rohr_1"].values()), 'c-',label="Geiger counter activity")
    ax.plot(x_axis_values,
            smoothed_data, 'r-', label="Smoothed Geiger counter activity")
    ax.legend(loc='upper right')
    plt.title(plot_title)
    ax.set_xlabel("Time ("+unit+")")
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

async def get_title(x_axis_mins:int):
    
    plot_title = str()
    if x_axis_mins < 60:
        plot_title = "Last "+str(x_axis_mins)+" minutes of data"
    elif x_axis_mins == 60:
        plot_title = "Last hour of data"

    elif x_axis_mins > 60 and x_axis_mins < 1440:
        hours = round(x_axis_mins/60,2)
        plot_title = "Last "+str(hours)+" hours of data"
    elif x_axis_mins == 1440:
        plot_title = "Last day of data"

    elif x_axis_mins > 1440 and x_axis_mins <10080:
        days = round(x_axis_mins/1440,2)
        plot_title = "Last "+str(days)+" days of data"
    elif x_axis_mins == 10080:
        plot_title = "Last week of data"

    elif x_axis_mins > 10080 and x_axis_mins < 43200:
        weeks = round(x_axis_mins/10080,2)
        plot_title = "Last "+str(weeks)+" weeks of data"
    elif x_axis_mins == 43200:
        plot_title = "Last month of data"

    elif x_axis_mins > 43200 and x_axis_mins < 525600:
        months = round(x_axis_mins/43200,2)
        plot_title = "Last "+str(months)+" months of data"
    elif x_axis_mins == 525600:
        plot_title = "Last year of data"

    elif x_axis_mins > 525600:
        years = round(x_axis_mins/525600,2)
        plot_title = "Last "+str(years)+" years of data"

    elif x_axis_mins == 2000000000:
        plot_title = "All data"
    return(plot_title)

async def label_x_axis_and_title(x_values:list):
    np_x_values = np.array(x_values)

    units = ["minutes","hours","days","weeks","months", "years"]
    breakpoints = [240,4320,30240,120960,1576800]
    # = [4h, 72h, 21d, 12w, 36m]
    dividing_values = [1,60,1440,10080,43200,525600]
    # 1h = 60min, 1d = 1440min, 1w = 10080min, 1M = 43200min, 1y = 525600min
    last_val = np_x_values[-1]

    div_factor = dividing_values[0]
    unit = units["minutes"]
    final_x_values = list(np_x_values)

    for i in reversed(range(6)):
        if last_val >= breakpoints[i-1]:
            unit = units[i]
            np_x_values = np_x_values/dividing_values[i]
            final_x_values = list(np_x_values)
            print(final_x_values)
            div_factor =dividing_values[i]
            break
    
    
    title_val = round(last_val/div_factor,2)
    title = "Last "+str(title_val)+" "+unit+" of data"

    return(final_x_values,unit,title,div_factor)
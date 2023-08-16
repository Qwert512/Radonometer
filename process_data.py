import time, math
from render import render

async def plot(json_data:dict,start_time_ms:int,x_width:float,y_height:float,x_axis_mins:int,minimum_x_len:int=2,dark_mode:bool=False):
    if x_axis_mins == 0:
        x_axis_mins = 2000000000
    if y_height < 1:
        y_height = 1
    if x_width < 1:
        x_width = 1
    #define some variables and fetch some basic data
    jumps_1 = ()
    jumps_2 = ()
    keys_1 = list(json_data["raw_minutes"]["rohr_1"].keys())
    keys_1 = list(map(int, keys_1))
    keys_2 = list(json_data["raw_minutes"]["rohr_2"].keys())
    keys_2 = list(map(int, keys_2))

    #?processing for "Rohr_1"
    #!deprecated sorting code, rework inc
    
    #Todo:
    #&json -> variable (done), -> keys(int) liste, 
    #?Werte sortieren -> Löcher füllen <2, (done)
    #?Einzelne Werte kicken < min_x_len (done), anpassen für Zeitfenster (done)
    #?Werte aus keys_1 in json forcen
    #?Offset Startwert vs 0 finden -> Subtrahieren von allen
    #?jumpms finden u Tuple bilden
    #?X-Axe labeln, div Faktor bekommen
    #?Tuples und Listen mit div_Faktor dividieren
    #?Plotten smd

    if True:
    # Werte sortieren
        keys_1 = sorted(keys_1)
        
        # Löcher füllen
        temp_keys = []
        for key in keys_1:
            if key - 1 not in keys_1 and key > 1:
                if key - 3 in keys_1 and key - 2 not in keys_1:
                    temp_keys.append(key - 2)

                if key - 2 in keys_1:
                    temp_keys.append(key - 1)
        temp_keys.extend(keys_1)
        keys_1 = sorted(temp_keys)

        #Einzelne kicken
        keys_1 = await remove_groups_smaller_than_min_x_len(keys_1=keys_1,min_x_len=minimum_x_len)
        last_key_1 = keys_1[len(keys_1)-1]
        first_key_1 = int(last_key_1) - x_axis_mins
        #Anpassen Werte auf Zeitfenster
        if first_key_1 <= 0:
            first_key_1 = 0
            offset = 0
            #check if it neccesary to remove values based on the provided time window
        else:
            # Anpassen Werte auf Zeitfenster
            keys_1 = [key for key in keys_1 if key >= first_key_1]
            offset = keys_1[0]

        #print(keys_1)
        #Erstellen y_values liste
        y_values=[]
        for i in range(len(keys_1)):
            if str(keys_1[i]) in json_data["raw_minutes"]["rohr_1"]:
                y_values.append(json_data["raw_minutes"]["rohr_1"][str(keys_1[i])])
            else:
                y_values.append(0)
        
        # get offset
        offset = keys_1[0]-1
        keys_1 = [num - offset for num in keys_1]

        jumps_1 = ()
        previous_num = keys_1[0]
        for i in range(len(keys_1) - 1):
            if int(keys_1[i+1]) > int(keys_1[i]) + 1:
                #print("Minute "+str(keys_1[i])+" = minute "+str(int(keys_1[i])-offset)+" from start")
                old_tuple = jumps_1
                new_tuple = old_tuple + ((previous_num, int(keys_1[i])),)
                previous_num = int(keys_1[i+1])
                jumps_1 = new_tuple
        old_tuple = jumps_1
        jumps_1 = old_tuple + ((previous_num, int(keys_1[i])),)
        #generate a tuple holding "jumps" for holes in the data

    x_values = keys_1

    time_elapsed_calc_ms = math.floor(time.time()*1000)-start_time_ms

    await render(dark_mode=dark_mode,x_width=x_width,y_height=y_height, jumps_1=jumps_1,json_data=json_data,x_values=x_values,start_time_ms=start_time_ms,time_elapsed_calc_ms=time_elapsed_calc_ms,y_values=y_values)

async def remove_groups_smaller_than_min_x_len(keys_1, min_x_len):
    result = []
    current_group = []
    
    for num in keys_1:
        if not current_group:
            current_group.append(num)
        elif num - current_group[-1] == 1:
            current_group.append(num)
        else:
            if len(current_group) >= min_x_len:
                result.extend(current_group)
            current_group = [num]

    if len(current_group) >= min_x_len:
        result.extend(current_group)
        
    return result

import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
minimum_x_len = 2

test_json_data = {
    "raw_minutes": {
        "rohr_1": {
            "1": 7,
            "2": 2,
            "3": 3,
            "4": 0,
            "25": 0,
            "26": 0,
            "783": 4,
            "784": 4,
            "804": 1,
            "805": 3,
            "806": 1,
            "807": 0,
            "808": 0,
            "809": 0,
            "810": 0,
            "811": 0,
            "812": 0,
            "813": 0
        },
        "rohr_2": {
            "1": 5,
            "2": 4,
            "3": 0,
            "4": 3,
            "25": 6,
            "783": 3,
            "804": 2,
            "806": 0,
            "807": 1,
            "808": 1,
            "809": 0,
            "810": 0,
            "811": 1,
            "812": 0,
            "813": 0
        }
    }
}

def plot(json_data:dict,x_width:float,y_height:float,x_axis_mins:int,minimum_x_len:int=2):
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

        previous_num = first_key_1
        for i in range(len(keys_1) - 1):
            if int(keys_1[i+1]) > int(keys_1[i]) + 1:
                old_tuple = jumps_1
                new_tuple = old_tuple + ((previous_num, int(keys_1[i])),)
                previous_num = int(keys_1[i+1])
                jumps_1 = new_tuple
        old_tuple = jumps_1
        jumps_1 = old_tuple + ((previous_num, int(keys_1[i])),)
        jumps_1 = [(a, b) for (a, b) in jumps_1 if abs(a - b) >= minimum_x_len]

        if int(keys_1[i]) == int(keys_1[i-1])+1:
            modified_tuple = [*jumps_1[-1][:-1], jumps_1[-1][-1] + 1]
            jumps_1 = tuple([list(t) if t != jumps_1[-1] else modified_tuple for t in jumps_1])

        #this is pretty complicated, just ignore it. It does some black magic and then the data is 
        #sorted, crisp, cleaned and stuffed into the right output format

    #processing for "Rohr_2"
    if True:

        if first_key_2 <= 0:
            first_key_2 = 0
            #see for the "rohr_1" code block
        else:
            for i in reversed(keys_2):
                i = int(i)

                if i < first_key_2:
                    json_data["raw_minutes"]["rohr_2"].pop(str(i))
                    keys_2.remove(str(i))


        previous_num = first_key_2
        for i in range(len(keys_2) - 1):
            if int(keys_2[i+1]) > int(keys_2[i]) + 1:
                old_tuple = jumps_2
                new_tuple = old_tuple + ((previous_num, int(keys_2[i])),)
                previous_num = int(keys_2[i+1])
                jumps_2 = new_tuple
        old_tuple = jumps_2
        jumps_2 = old_tuple + ((previous_num, int(keys_2[i])),)
        jumps_2 = [(a, b) for (a, b) in jumps_2 if abs(a - b) >= minimum_x_len]

        if int(keys_2[i]) == int(keys_2[i-1])+1:
            modified_tuple = [*jumps_2[-1][:-1], jumps_2[-1][-1] + 1]
            jumps_2 = tuple([list(t) if t != jumps_2[-1] else modified_tuple for t in jumps_2])

    # Create a figure and axes

    plt.figure(figsize=(x_width, y_height),dpi=120)
    ax = brokenaxes(xlims=jumps_1, hspace=0.05)

    # Plot data on the broken axes
    ax.plot([int(x) for x in list(json_data["raw_minutes"]["rohr_1"].keys())],
            list(json_data["raw_minutes"]["rohr_1"].values()), 'b-',label="Geiger counter activity")
    ax.legend(loc='upper right')
    plt.title("Last "+str(x_axis_mins)+" minutes of Data")
    ax.set_xlabel("Time (mins)")
    ax.set_ylabel("Activity (CPM)")


    # Show the plot
    plt.savefig("last_x_mins.png")
    plt.clf()
    plt.close()
plot(test_json_data,12,8,890,2)
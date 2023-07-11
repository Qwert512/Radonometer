import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
minimum_x_len = 2

json_data = {
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


# Calculate the "jumps" in the x-axis
jumps_1 = ()
jumps_2 = ()
keys_1 = list(json_data["raw_minutes"]["rohr_1"].keys())
keys_2 = list(json_data["raw_minutes"]["rohr_2"].keys())


previous_num = 1
for i in range(len(keys_1) - 1):
    if int(keys_1[i+1]) > int(keys_1[i]) + 1:
        old_tuple = jumps_1
        new_tuple = old_tuple + ((previous_num, int(keys_1[i])),)  # Create a new tuple with two elements
        previous_num = int(keys_1[i+1])
        jumps_1 = new_tuple
old_tuple = jumps_1
jumps_1 = old_tuple + ((previous_num, int(keys_1[i])),)
jumps_1 = [(a, b) for (a, b) in jumps_1 if abs(a - b) >= minimum_x_len]


previous_num = 1
for i in range(len(keys_2) - 1):
    if int(keys_2[i+1]) > int(keys_2[i]) + 1:
        old_tuple = jumps_2
        new_tuple = old_tuple + ((previous_num, int(keys_2[i])),)  # Create a new tuple with two elements
        previous_num = int(keys_2[i+1])
        jumps_2 = new_tuple
old_tuple = jumps_2
jumps_2 = old_tuple + ((previous_num, int(keys_2[i])),)
jumps_2 = [(a, b) for (a, b) in jumps_2 if abs(a - b) >= minimum_x_len]



print(jumps_1)
print(jumps_2)

# Create a figure and axes

fig = plt.figure(figsize=(6, 4))
ax = brokenaxes(xlims=jumps_1, hspace=0.05)

# Plot data on the broken axes
ax.plot([int(x) for x in list(json_data["raw_minutes"]["rohr_1"].keys())],
        list(json_data["raw_minutes"]["rohr_1"].values()), 'b-')

# Show the plot
plt.show()
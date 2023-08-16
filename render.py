import time, math
import numpy as np
import matplotlib.pyplot as plt
from brokenaxes import brokenaxes
from cycler import cycler

dark_mode_color = '#282828'

mpl_dark = {
            'axes.facecolor'    : dark_mode_color,
            'axes.labelcolor'   : 'white',
            'axes.edgecolor'    : 'white',
            'figure.facecolor'  : dark_mode_color,
            'figure.edgecolor'  : '#808080',
            'savefig.facecolor' : dark_mode_color,
            'savefig.edgecolor' : dark_mode_color,
            'xtick.color'       : 'white',
            'ytick.color'       : 'white',
            'text.color'        : 'white',
            'grid.color'        : '#CCCCCC',
            'axes.prop_cycle'   : cycler('color', ['r', 'g', 'c', 'm', 'y', 'w'])
            }

mpl_light = {
            'axes.facecolor'    : 'white',
            'axes.labelcolor'   : 'black',
            'axes.edgecolor'    : 'black',
            'figure.facecolor'  : 'white',
            'figure.edgecolor'  : '#808080',
            'savefig.facecolor' : 'white',
            'savefig.edgecolor' : 'white',
            'xtick.color'       : 'black',
            'ytick.color'       : 'black',
            'text.color'        : 'black',
            'grid.color'        : '#222222',
            'axes.prop_cycle'   : cycler('color', ['r', 'b', 'c', 'm', 'k'])
            }


async def render(dark_mode:bool,x_width:int,y_height:int,jumps_1:tuple,json_data:dict,x_values:list,start_time_ms:int,time_elapsed_calc_ms:int,y_values:list):
    x_axis_values, unit, plot_title, div_val = await label_x_axis_and_title(x_values=x_values)
    
    jumps_1 = tuple([list(map(lambda val: val / div_val, sublist)) for sublist in jumps_1])
    #divide all values in the jumps 1 tuple by the div values provided

    # convert all  minute values from str to int and substract the start value from them, so the diagram starts at 0
    
    window_size = min(10, len(y_values))  # Use a window size of 10 or the length of the data array, whichever is smaller
    smoothed_data = np.convolve((y_values), np.ones(window_size) / window_size, mode='same')
    # Plot data on the broken axes

    
    style_context = mpl_dark if dark_mode else mpl_light

    with plt.style.context(style_context):
        plt.figure(figsize=(x_width, y_height), dpi=120)

        if len(jumps_1) != 0:
            ax = brokenaxes(xlims=jumps_1, hspace=0.05)
            ax.plot(x_axis_values, y_values, 'c-', label="Geiger counter activity")
            ax.plot(x_axis_values, smoothed_data, 'r-', label="Smoothed Geiger counter activity")
        else:
            ax = brokenaxes(hspace=0.05)
            print("Plotting NO data")

        ax.set_xlabel("Time (" + unit + ")")
        ax.set_ylabel("Activity (CPM)")
        ax.legend(loc='upper right')
        plt.title(plot_title)
    # Save the plot
    plt.savefig("last_x_mins.png")
    plt.clf()
    plt.close()

    time_elapsed_render_ms = math.floor(time.time()*1000) - start_time_ms - time_elapsed_calc_ms
    time_diff_ms = time_elapsed_calc_ms+time_elapsed_render_ms
    render_time_percent = round((time_elapsed_render_ms/time_diff_ms)*100,2)
    calc_time_percent = round((time_elapsed_calc_ms/time_diff_ms)*100,2)

    print("Successfully updated all plots in "+str(time_diff_ms)+"ms. Off that rendering took up "
          +str(time_elapsed_render_ms)+"ms ("+str(render_time_percent)+"%) and processing took up "
          +str(time_elapsed_calc_ms)+"ms ("+str(calc_time_percent)+"%)")
   

async def label_x_axis_and_title(x_values:list):
    np_x_values = np.array(x_values)

    units = ["minutes","hours","days","weeks","months", "years"]
    breakpoints = [240,4320,30240,120960,1576800]
    # = [4h, 72h, 21d, 12w, 36m]
    dividing_values = [1,60,1440,10080,43200,525600]
    # 1h = 60min, 1d = 1440min, 1w = 10080min, 1M = 43200min, 1y = 525600min
    last_val = np_x_values[-1]

    div_factor = dividing_values[0]
    unit = units[0]
    final_x_values = list(np_x_values)

    for i in reversed(range(6)):
        if last_val >= breakpoints[i-1]:
            unit = units[i]
            np_x_values = np_x_values/dividing_values[i]
            final_x_values = list(np_x_values)
            div_factor =dividing_values[i]
            break
    
    
    title_val = round(last_val/div_factor,2)
    title = "Last "+str(title_val)+" "+unit+" of data"
    return(final_x_values,unit,title,div_factor)

 
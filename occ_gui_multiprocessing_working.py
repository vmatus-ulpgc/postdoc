#graphical user interface for optical camerca communication experimentation
#by vicente matus (vmatus@idetic.eu), idetic-ulpgc, gran canaria, spain.
#in collaboration with eleni niarchou (eleni.niarchou@ulpgc.es)

#################
#### imports ####
#################

import picamera #raspberry's camera
import picamera.array #capture images in RGB matrix mode
from picamera import mmal, mmalobj, exc #included for setting the analog/digital gain
from picamera.mmalobj import to_rational #included for setting the analog/digital gain
#from io import BytesIO #library for handling streams
import time
import tkinter #graphic user interfaces
import numpy as np#vectors, matrices, etc.
import PIL #python imaging library!!!
from PIL import ImageTk
#import matplotlib #plots like matlab
from matplotlib.figure import Figure
#tell matlab to use tkinter backend:
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import multiprocessing as mp

##########################
#### global variables ####
##########################

global stream
global canvas_capture
global input_image
global cam_cap
global image_on_canvas
global fig
global canvas_plot

####################
#### parameters ####
####################

MMAL_PARAMETER_ANALOG_GAIN = mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x59 #included for setting the analog/digital gain
MMAL_PARAMETER_DIGITAL_GAIN = mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x5A #included for setting the analog/digital gain

scaling_factor = 5
width = 2592
height = 1952
#initialize roi as one single column:
roi = int(width/2)#column of interest TODO: expand ROI to [x,y,w,h]

input_path='/home/pi/Desktop/occ_gui/app/'
output_path='/home/pi/Desktop/occ_gui/results/'


root = tkinter.Tk() #root tkinter window
root.geometry("1200x700")
#root.geometry("800x480") #official 7-inch display's resolution
root.title("occ gui by vmatus and eleni niarchou")


#### WINDOW SHAPE ####

# titles / quit button   <--- top frame
# camera frame / plot    <--- center frame
# camera params. / log text < bottom frame

top_frame = tkinter.Frame(root)
tkinter.Label(top_frame, text="optical camera communication (occ) graphical user interface").pack(side=tkinter.LEFT)
top_frame.pack(side=tkinter.TOP)

center_frame = tkinter.Frame(root)
center_frame.pack(side=tkinter.TOP)

bottom_frame = tkinter.Frame(root)
#tkinter.Label(bottom_frame, text="bottom frame").pack(side=tkinter.LEFT)
bottom_frame.pack(side=tkinter.TOP)

params_frame = tkinter.Frame(bottom_frame)
#tkinter.Label(bottom_frame, text="camera parameters:").pack(side=tkinter.TOP)
params_frame.pack(side=tkinter.LEFT)

logs_frame = tkinter.Frame(bottom_frame)
#tkinter.Label(bottom_frame, text="to be defined...").pack(side=tkinter.LEFT)
logs_frame.pack(side=tkinter.LEFT)
tkinter.Text(logs_frame, height = 6, width = 50).pack(side=tkinter.TOP)

canvas_capture = tkinter.Canvas(center_frame,width=width/scaling_factor,height=height/scaling_factor)
canvas_capture.pack(side=tkinter.LEFT)
mysuperwellidentifiedline = canvas_capture.create_line(0,0,1,1) #temporary dot to be erased

#parameters: t_exp, fps, g_analog, g_digital, g_blue, g_red
params_array = [0]*6#[t_exp, fps, ag, dg, rg, bg]
params_defaults = [333,30,1.0,1.0,1.090,1.711]#[t_exp, fps, ag, dg, rg, bg]
params_names = ["exposure time (μs)","framerate (fps)","analog gain (·)","digital gain (·)","red gain (·)","blue gain (·)"]
#params_subframes = [tkinter.Frame(params_frame)]*6
params_textboxes = list()
params_sliders = list()
params_scales_min = [85,0.1666,1,1,1,1]
params_scales_max = [33333,90,10.66,15.8489,5,5] #TODO: check real gain values 

for i in range(len(params_array)):
    #create label:
    tkinter.Label(params_frame, text=params_names[i]).grid(row=i,column=0)
    #create text box:
    textbox = tkinter.Text(params_frame, height = 1, width = 5)
    textbox.grid(row=i,column=1)
    textbox.insert(1.0,str(params_defaults[i]))
    params_textboxes.append(textbox)
    #create slider (tk.Scale()):
    slider = tkinter.Scale(params_frame,
                          from_=params_scales_min[i],
                          to=params_scales_max[i],
                          orient='horizontal',
                          #variable=params_array[i],
                          showvalue=0)
    slider.set(params_defaults[i])
    slider.grid(row=i,column=2)
    params_sliders.append(slider)
    # :)

def set_params():
    print("camera parameters set to:")
    for i in range(len(params_array)):
        print(params_names[i],": ",params_sliders[i].get())
set_params_button = tkinter.Button(master=params_frame, text="set", command=set_params).grid(column=3, rowspan=3,row=2)
    
#parameters_2: roi

#######################
#### capture image ####
#######################

#exposure time (microseconds)
#analog gain (factor)
#digital gain (factor)
#lenght of video (milliseconds)
#white balance
#region of interest
#frame rate (fps)

#image = parent.get()

#######################
#### signals plots ####
#######################

def refresh_plots(roi): #for now roi is a column, which is in [0 to max horizontal resolution]
    column = roi
    rx_signal = stream_array[:,column,:] #pixel values at column x
    fig.clf() #clear figure
    #plot R,G,B:
    fig.add_subplot(311).plot(t,rx_signal[:,0],linewidth=0.5,color='r')
    ax = fig.gca()
    ax.grid()
    ax.set_ylim((0,255))
    ax.set_title("Signal plots for column {}".format(column))
    ax.set_ylabel("Pixel value")
    ax.tick_params(axis='x',          # changes apply to the x-axis
                   which='both',      # both major and minor ticks are affected
                   bottom=False,      # ticks along the bottom edge are off
                   top=False,         # ticks along the top edge are off
                   labelbottom=False) # labels along the bottom edge are off
    fig.add_subplot(312).plot(t,rx_signal[:,1],linewidth=0.5,color='g')
    ax = fig.gca()
    ax.grid()
    ax.set_ylim((0,255))
    ax.set_ylabel("Pixel value")
    ax.tick_params(axis='x',          # changes apply to the x-axis
                   which='both',      # both major and minor ticks are affected
                   bottom=False,      # ticks along the bottom edge are off
                   top=False,         # ticks along the top edge are off
                   labelbottom=False) # labels along the bottom edge are off
    fig.add_subplot(313).plot(t,rx_signal[:,2],linewidth=0.5,color='b')
    ax = fig.gca()
    ax.grid()
    ax.set_ylim((0,255))
    ax.set_ylabel("Pixel value")
    ax.set_xlabel("Time (microsec)")
    canvas_plot.draw() #refresh the canvas
    #and create the new line (at x-coordinate where the user clicked)
    global mysuperwellidentifiedline #vertical dashed line to be analized
    print("creating new dashed line")
    canvas_capture.delete(mysuperwellidentifiedline)
    mysuperwellidentifiedline = canvas_capture.create_line(column/scaling_factor, 0, column/scaling_factor,
                                                           int(height/scaling_factor),
                                                           dash=(4, 2),
                                                           fill='yellow')
    canvas_capture.line = mysuperwellidentifiedline
    print(mysuperwellidentifiedline)
    
def frame_grabbing(connection):
    #function to parallelize. it receives the child Pipe connection and the PiCamera object
    #it returns (constantly) RGB images into the pipe
    #params_defaults = [333,30,1,1,1.090,1.711]#[t_exp, fps, ag, dg, rg, bg]
    camera = picamera.PiCamera() #start the camera as a PiCamera object
    #global stream
    stream = picamera.array.PiRGBArray(camera) #create a PiRGBArray stream object
    print("setting default camera parameters")
    camera.resolution = (width,height) #set resolution (width,height) in pixels
    camera.shutter_speed = params_defaults[0] #set exposure time in microseconds
    camera.framerate = params_defaults[1]#set framerate in fps
    #camera.analog_gain = params_defaults[2]
    #camera.digital_gain = params_defaults[3]
    mmal.mmal_port_parameter_set_rational(camera._camera.control._port, 
                                          MMAL_PARAMETER_ANALOG_GAIN ,
                                          to_rational(params_defaults[2]))
    mmal.mmal_port_parameter_set_rational(camera._camera.control._port, 
                                          MMAL_PARAMETER_DIGITAL_GAIN ,
                                          to_rational(params_defaults[3]))
    camera.awb_mode = 'off'
    camera.awb_gains = (params_defaults[4],params_defaults[5])
    print("done setting camera parameters")
    #while True:
    for i in range(3):
        print("taking photo")
        stream.truncate(0) #clear the stream object
        camera.capture(stream, 'rgb') #make a capture
        connection.send(stream.array) #put the rgb matrix in the pipe

def callback(event):
    #print("clicked at: ", event.x*scaling_factor, event.y*scaling_factor)
    global roi
    roi=event.x*scaling_factor
    refresh_plots(event.x*scaling_factor)
    #end of callback function
    
canvas_capture.bind("<Button-1>", callback)

fig = Figure() #create the plot figure
delta_t = 18.904 #rolling shutter delta t in microseconds
roi = int(width/2)#column of interest TODO: expand ROI to [x,y,w,h]
t = np.arange(0,height*delta_t,delta_t) #the relative time of each pixel row
canvas_plot = FigureCanvasTkAgg(fig, master = center_frame) #tkinter canvas
canvas_plot.draw() 
canvas_plot.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1) #pack the canvas in the window


#time.sleep(10)

    




def take_photo_old():
    stream.truncate(0)
    #camera.start_preview() #overlay the camera input ***warning***: must use stop_preview() afterwards
    camera.capture(stream, 'rgb') #save a photograph as raw RGB format matrix
    #camera.stop_preview() #must do if you did start_preview()
    input_image = PIL.Image.fromarray(stream.array)
    input_image_resized = input_image.resize((int(width/scaling_factor),
                                              int(height/scaling_factor)),
                                             PIL.Image.ANTIALIAS)
    cam_cap = ImageTk.PhotoImage(input_image_resized)
    canvas_capture.itemconfig(image_on_canvas,image=cam_cap)
    canvas_capture.image = cam_cap
    canvas_capture.update_idletasks()
    refresh_plots(roi)
    #end of take_photo function
    
#shutter_button = tkinter.Button(master=params_frame, text="take new photo", command=take_photo, anchor='w')
#shutter_button.pack(side=tkinter.LEFT)

def _quit():
    #frame_streamer.join()
    root.quit()
    root.destroy()
    
button_quit = tkinter.Button(master=top_frame, text="close occ gui", command=_quit, anchor='e')
button_quit.pack(side=tkinter.RIGHT)

parent, child = mp.Pipe()
#frame_streamer = mp.Process(target = frame_grabbing, args=(child,))

pool = mp.Pool(processes=1)
frame_streamer = pool.apply_async(frame_grabbing,(child,))

#frame_streamer.start()

for i in range(3):
#    take_photo()
#def take_photo():
    stream_array = parent.recv()
    print("fetched image of resolution: ", np.shape(stream_array))
    input_image = PIL.Image.fromarray(stream_array) #transform 
    #input_image = PIL.Image.fromarray(parent.recv())
    cam_cap = ImageTk.PhotoImage(input_image.resize((int(width/scaling_factor),int(height/scaling_factor)),PIL.Image.ANTIALIAS))
    image_on_canvas = canvas_capture.create_image(0, 0, anchor=tkinter.NW, image=cam_cap)
    canvas_capture.itemconfig(image_on_canvas,image=cam_cap)
    canvas_capture.image = cam_cap
    canvas_capture.update_idletasks()
    refresh_plots(roi)
refresh_plots(roi) #(re)draw the plots at the (column) region of interest

#####################
#### end of code ####
#####################

tkinter.mainloop()


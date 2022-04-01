#graphical user interface for optical camerca communication experimentation
#by vicente matus (vmatus@idetic.eu), idetic-ulpgc, gran canaria, spain.
#in collaboration with eleni niarchou (eleni.niarchou@ulpgc.es)

#################
#### imports ####
#################

import picamera #raspberry's camera
import picamera.array #capture images in RGB matrix mode
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


input_path='/home/pi/Desktop/occ_gui/app/'
output_path='/home/pi/Desktop/occ_gui/results/'


root = tkinter.Tk() #root tkinter window
root.geometry("1200x600")
root.title("occ gui")


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
tkinter.Label(bottom_frame, text="bottom frame").pack(side=tkinter.LEFT)
bottom_frame.pack(side=tkinter.TOP)

params_frame = tkinter.Frame(bottom_frame)
tkinter.Label(bottom_frame, text="camera parameters:").pack(side=tkinter.LEFT)
params_frame.pack(side=tkinter.LEFT)

logs_frame = tkinter.Frame(bottom_frame)
tkinter.Label(bottom_frame, text="to be defined...").pack(side=tkinter.LEFT)
logs_frame.pack(side=tkinter.LEFT)

#######################
#### capture image ####
#######################

global stream
global canvas_capture
global input_image
global cam_cap
global image_on_canvas
global fig
global canvas_plot

#exposure time (microseconds)
#analog gain (factor)
#digital gain (factor)
#lenght of video (milliseconds)
#white balance
#region of interest
#frame rate (fps)

#image = parent.get()

scaling_factor = 4
width = 2592
height = 1952
#initialize roi as one single column:
roi = int(width/2)#column of interest TODO: expand ROI to [x,y,w,h]

def frame_grabbing(connection):
    #function to parallelize. it receives the child Pipe connection and the PiCamera object
    #it returns (constantly) RGB images into the pipe
    camera = picamera.PiCamera() #start the camera as a PiCamera object
    #global stream
    stream = picamera.array.PiRGBArray(camera) #create a PiRGBArray stream object
    camera.resolution = (width,height) #set resolution (width,height) in pixels
    camera.framerate = 30 #set framerate in fps
    camera.shutter_speed = 333 #set exposure time in microseconds
    #while True:
    for i in range(10):
        print("fetching image")
        stream.truncate(0) #clear the stream object
        camera.capture(stream, 'rgb') #make a capture
        connection.send(stream.array) #put the rgb matrix in the pipe

parent, child = mp.Pipe()
frame_streamer = mp.Process(target = frame_grabbing, args=(child,))
frame_streamer.start()
time.sleep(10)
for i in range(10):
    stream_array = parent.recv()
    print(np.shape(stream_array))
frame_streamer.join()

input_image = PIL.Image.fromarray(stream_array) #transform 
#input_image = PIL.Image.fromarray(parent.recv())
canvas_capture = tkinter.Canvas(center_frame,width=width/scaling_factor,height=height/scaling_factor)
canvas_capture.pack(side=tkinter.LEFT)

cam_cap = ImageTk.PhotoImage(input_image.resize((int(width/scaling_factor),int(height/scaling_factor)),PIL.Image.ANTIALIAS))
image_on_canvas = canvas_capture.create_image(0, 0, anchor=tkinter.NW, image=cam_cap)
mysuperwellidentifiedline = canvas_capture.create_line(0,0,1,1)


def take_photo():
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

def callback(event):
    print("clicked at: ", event.x*scaling_factor, event.y*scaling_factor)
    global roi
    roi=event.x*scaling_factor
    refresh_plots(event.x*scaling_factor)
    #end of callback function
    
canvas_capture.bind("<Button-1>", callback)

#######################
#### signals plots ####
#######################

def refresh_plots(roi): #for now roi is a column, which is in [0 to max horizontal resolution]
    column = roi
    rx_signal = stream_array[:,column,:] #pixel values at column x
    fig.clf() #clear figure
    #plot R,G,B:
    fig.add_subplot(311).plot(t,rx_signal[:,0],'r')
    ax = fig.gca()
    ax.set_ylim((0,255))
    fig.add_subplot(312).plot(t,rx_signal[:,1],'g')
    ax = fig.gca()
    ax.set_ylim((0,255))
    fig.add_subplot(313).plot(t,rx_signal[:,2],'b')
    ax = fig.gca()
    ax.set_ylim((0,255))
    canvas_plot.draw() #refresh the canvas
    #and create the new line (at x-coordinate where the user clicked)
    global mysuperwellidentifiedline #vertical dashed line to be analized
    canvas_capture.delete(mysuperwellidentifiedline)
    mysuperwellidentifiedline = canvas_capture.create_line(column/scaling_factor, 0, column/scaling_factor,
                                                           int(height/scaling_factor),
                                                           dash=(4, 2),
                                                           fill='yellow')

fig = Figure() #create the plot figure
delta_t = 18.904 #rolling shutter delta t in microseconds
roi = int(width/2)#column of interest TODO: expand ROI to [x,y,w,h]
t = np.arange(0,height*delta_t,delta_t) #the relative time of each pixel row
canvas_plot = FigureCanvasTkAgg(fig, master = center_frame) #tkinter canvas
canvas_plot.draw() 
canvas_plot.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1) #pack the canvas in the window
refresh_plots(roi) #(re)draw the plots at the (column) region of interest

def _quit():
    root.quit()
    root.destroy()
    
button_quit = tkinter.Button(master=top_frame, text="close occ gui", command=_quit, anchor='e')
button_quit.pack(side=tkinter.RIGHT)

#####################
#### end of code ####
#####################

tkinter.mainloop()

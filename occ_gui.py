#graphical user interface for optical camerca communication experimentation
#by vicente matus (vmatus@idetic.eu), idetic-ulpgc, gran canaria, spain.
#in collaboration with eleni niarchou (eleni.niarchou@ulpgc.es)

#################
#### imports ####
#################

import picamera #raspberry's camera
import picamera.array #capture images in RGB matrix mode
from io import BytesIO #library for handling streams
import time
import tkinter #graphic user interfaces
import numpy as np#vectors, matrices, etc.
import PIL #python imaging library!!!
from PIL import ImageTk
#import matplotlib #plots like matlab
from matplotlib.figure import Figure
#tell matlab to use tkinter backend:
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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

#exposure time (microseconds)
#analog gain (factor)
#digital gain (factor)
#lenght of video (milliseconds)
#white balance
#region of interest
#frame rate (fps)

camera = picamera.PiCamera() #start the camera as a PiCamera object
#stream = BytesIO()
global stream
stream = picamera.array.PiRGBArray(camera) #create a PiRGBArray stream object
camera.resolution = (2592,1952) #set resolution (width,height) in pixels
camera.framerate = 30 #set framerate in fps
camera.shutter_speed = 333 #set exposure time in microseconds
scaling_factor = 4
global canvas_capture
global input_image
global cam_cap
global image_on_canvas
canvas_capture = tkinter.Canvas(center_frame,width=camera.resolution[0]/scaling_factor,height=camera.resolution[1]/scaling_factor)
canvas_capture.pack(side=tkinter.LEFT)

camera.capture(stream, 'rgb')
input_image = PIL.Image.fromarray(stream.array)
cam_cap = ImageTk.PhotoImage(input_image.resize((int(camera.resolution[0]/scaling_factor),int(camera.resolution[1]/scaling_factor)),PIL.Image.ANTIALIAS))
image_on_canvas = canvas_capture.create_image(0, 0, anchor=tkinter.NW, image=cam_cap)

def take_photo():
    stream.truncate(0)

    #canvas_capture.delete('all')
    #camera.start_preview() #overlay the camera input ***warning***: must use stop_preview() afterwards
    #time.sleep(2) #warm up time of the camera
    camera.capture(stream, 'rgb') #save a photograph as raw RGB format matrix
    #print(stream.array)
    #stram.array is the matrix of the photograph in numpy format
    #camera.stop_preview() #must do if you did start_preview()

    #input_image = PIL.Image.open(input_path+'test_hq_cam.jpeg')
    input_image = PIL.Image.fromarray(stream.array)
    #print(input_image)
    input_image_resized = input_image.resize((int(camera.resolution[0]/scaling_factor),
                                              int(camera.resolution[1]/scaling_factor)),
                                             PIL.Image.ANTIALIAS)
    
    cam_cap = ImageTk.PhotoImage(input_image_resized)
    #print(cam_cap)
    #canvas_capture = tkinter.Canvas(center_frame,width=camera.resolution[0]/scaling_factor,height=camera.resolution[1]/scaling_factor)
    #image_on_canvas = canvas_capture.create_image(0, 0, anchor=tkinter.NW, image=cam_cap)
    #print(image_on_canvas)
    canvas_capture.itemconfig(image_on_canvas,image=cam_cap)
    canvas_capture.image = cam_cap
    canvas_capture.update_idletasks()
    print(canvas_capture)
    
    #tkinter.Label(center_frame, image=cam_cap).pack(side=tkinter.RIGHT, expand='yes')

#take_photo()

#def take_photo():
    #stream.truncate(0)
    #camera.capture(stream, 'rgb')
    #print("I just took a new photo!")
    #new_input_image = PIL.Image.fromarray(stream.array)
    #global cam_cap
    #new_cap = ImageTk.PhotoImage(new_input_image.resize((int(camera.resolution[0]/scaling_factor),int(camera.resolution[1]/scaling_factor)),PIL.Image.ANTIALIAS))
    #cam_cap.configure(image=new_cap)
    #global image_on_canvas
    #canvas_capture.itemconfigure(image_on_canvas, image=new_cap)
    #canvas_capture.delete(image_on_canvas)
    #image_on_canvas = canvas_capture.create_image(0, 0, anchor=tkinter.NW, image=new_cap)


shutter_button = tkinter.Button(master=params_frame, text="take new photo", command=take_photo, anchor='w')
shutter_button.pack(side=tkinter.LEFT)

def callback(event):
    print("clicked at: ", event.x*scaling_factor, event.y*scaling_factor)
    global mysuperwellidentifiedline
    canvas_capture.delete(mysuperwellidentifiedline)
    mysuperwellidentifiedline = canvas_capture.create_line(event.x, 0, event.x, int(camera.resolution[1]/scaling_factor), dash=(4, 2), fill='yellow')
    rx_signal = stream.array[:,event.x*scaling_factor,:]
    fig.clf()
    fig.add_subplot(311).plot(t,rx_signal[:,0],'r')
    ax = fig.gca()
    ax.set_ylim((0,255))
    fig.add_subplot(312).plot(t,rx_signal[:,1],'g')
    ax = fig.gca()
    ax.set_ylim((0,255))
    fig.add_subplot(313).plot(t,rx_signal[:,2],'b')
    ax = fig.gca()
    ax.set_ylim((0,255))
    canvas_plot.draw()
canvas_capture.bind("<Button-1>", callback)
mysuperwellidentifiedline = canvas_capture.create_line(0,0,1,1)


#######################
#### signals plots ####
#######################

fig = Figure()

delta_t = 18.904 #microseconds
t = np.arange(0,camera.resolution[1]*delta_t,delta_t)
rx_signal = stream.array[:,2028,:]
fig.add_subplot(311).plot(t,rx_signal[:,0],'r')
ax = fig.gca()
ax.set_ylim((0,255))
fig.add_subplot(312).plot(t,rx_signal[:,1],'g')
ax = fig.gca()
ax.set_ylim((0,255))
fig.add_subplot(313).plot(t,rx_signal[:,2],'b')
ax = fig.gca()
ax.set_ylim((0,255))

canvas_plot = FigureCanvasTkAgg(fig, master = center_frame)
canvas_plot.draw()
canvas_plot.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)



def _quit():
    root.quit()
    root.destroy()
    
button_quit = tkinter.Button(master=top_frame, text="close occ gui", command=_quit, anchor='e')
button_quit.pack(side=tkinter.RIGHT)

tkinter.mainloop()

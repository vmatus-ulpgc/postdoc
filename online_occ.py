# source: https://pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
#################
#### imports ####
#################
from picamera.array import PiRGBArray
from picamera import PiCamera
from picamera import mmal, mmalobj, exc #included for setting the analog/digital gain
from picamera.mmalobj import to_rational #included for setting the analog/digital gain
import numpy as np #vectors, matrices, etc.
import time
import cv2 #openCV!!!!

##########################
#### global variables ####
##########################

global roi_start_point
global roi_end_point


first_click = True

####################
#### parameters ####
####################

MMAL_PARAMETER_ANALOG_GAIN = mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x59 #included for setting the analog/digital gain
MMAL_PARAMETER_DIGITAL_GAIN = mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x5A #included for setting the analog/digital gain


#width = 2592
#height = 1952

width = 640
height = 480

roi = [0,0,width,height]
roi_start_point = (roi[0],roi[1])
roi_end_point = (roi[0]+roi[2]-1,roi[1]+roi[3]-1)

input_path='/home/occ/Desktop/occ_proc/app/'
output_path='/home/occ/Desktop/occ_proc/results/'

params_defaults = [333,30,1.0,1.0,1.090,1.711]#[t_exp, fps, ag, dg, rg, bg]
params_array = params_defaults
params_names = ["exposure time (μs)","framerate (fps)","analog gain (·)","digital gain (·)","red gain (·)","blue gain (·)"]
params_scales_min = [85,0.1666,1.0,1.0,0.0,0.0]
params_scales_max = [33333,90.0,10.66,15.8489,2.0,2.0] #TODO: check real gain values



###################
#### functions ####
###################

def set_cam_parameters(): #params_array = [t_exp, fps, ag, dg, rg, bg]

    print("setting camera parameters")
    camera.resolution = (width,height) #set resolution (width,height) in pixels
    camera.shutter_speed = params_array[0] #set exposure time in microseconds
    camera.framerate = params_array[1]#set framerate in fps
    #camera.analog_gain = params_defaults[2]
    #camera.digital_gain = params_defaults[3]
    mmal.mmal_port_parameter_set_rational(camera._camera.control._port, 
                                          MMAL_PARAMETER_ANALOG_GAIN ,
                                          to_rational(params_array[2]))
    mmal.mmal_port_parameter_set_rational(camera._camera.control._port, 
                                          MMAL_PARAMETER_DIGITAL_GAIN ,
                                          to_rational(params_array[3]))
    camera.awb_mode = 'off'
    camera.awb_gains = (params_array[4],params_array[5])
    print("done setting camera parameters")
    
def roi_click(event,x,y,flags,param):
    
    global first_click
    global roi_start_point
    global roi_end_point
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if first_click:
            roi_start_point = (x,y)
            print("roi start point set to:",x,y)
            first_click = False
        else:
            roi_end_point = (x,y)
            print("roi end point set to:",x,y)
            first_click = True

##############
#### MAIN ####
##############

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
set_cam_parameters()
rawCapture = PiRGBArray(camera, size=(width, height))
# allow the camera to warmup
time.sleep(0.1)

# create the window
cv2.namedWindow('occ_proc')
cv2.setMouseCallback('occ_proc',roi_click)

# capture frames from the camera

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	
	###########################
	#### OCC PROCESSING!!! ####
	###########################
	
	
	#user-defined roi on mouse clicks TODO: roi detection
	#roi = (x,y,w,h)
	
	# display the detected roi
	image = cv2.rectangle(image, roi_start_point, roi_end_point, (50,255,171))
	
	###################################
	#### rolling shutter detection ####
	###################################
	# average
	
	# equalization
	
	# threshold
	
	##################################
	#### global shutter detection ####
	##################################
	
	# phase detection
	
	# equalization
	
	# threshold
	
	
	# show the frame
	cv2.imshow('occ_proc', image)
	
	key = cv2.waitKey(1) & 0xFF
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
cv2.destroyAllWindows()

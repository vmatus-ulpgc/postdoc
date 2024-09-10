import numpy as np
from scipy.signal import decimate
import cv2
import timeit

import multiprocessing
import sys
import collections

import matplotlib.pyplot as plt
plt.switch_backend('QT5Agg')
#import matplotlib.animation as animation

font = cv2.FONT_HERSHEY_SIMPLEX

# process flags
PROCESS_READY = (1, 1)
PROCESS_BUSY = (2, 2)
PROCESS_SHUTDOWN = (3, 3)

global mouse_x
global mouse_y

def define_xy(event,x,y,flags,param):
    global mouse_x,mouse_y
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_x,mouse_y = x,y

def CameraProcess(pipe): #frame stream process
    #cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture('https://192.168.137.149:4343/video')
    # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0)
    # cap.set(cv2.CAP_PROP_EXPOSURE,-6)
    # cap.set(cv2.CAP_PROP_GAIN,5)
    
    cap = cv2.VideoCapture("C:\\Users\\Y6082772\\Desktop\\OLD\\2024balkancom-sccppam\\2024-04-19-sccppam-15m.h264")
    
    # cap = cv2.VideoCapture("C:/Users/Y6082772/Desktop/occ_pam/resultados/test-3332.h264")
    # cap = cv2.VideoCapture("C:/Users/Y6082772/Desktop/occ_pam/resultados/occ_pam_video_2023-05-19_18-01-01_exposure_333.h264")
    # cap = cv2.VideoCapture("D:/research_data/2023/IT2_atmosChamber/captures/test_front_roi_60C.h264")
    # cap = cv2.VideoCapture("C:/Users/Y6082772/Downloads/occ_pam_video_2023-05-25_09-01-01_exposure_333.h264")
    # video_name = "rx1_video_2023-03-15_15-59-27_exposure_33333"
    # cap = cv2.VideoCapture("D:/research_data/2023/NU_STSM/rx1/"+video_name+".h264")
    # cap = cv2.VideoCapture("G:/othman_stsm/othman_mode3.h264")
    # cap = cv2.VideoCapture("D:/research_data/2023/2023_02_23_caps/final_test.h264")
    # cap = cv2.VideoCapture("D:/research_data/2023/IT2_atmosChamber/captures/test_front_roi_60C.h264")
    # cap = cv2.VideoCapture("E:/research_data/NU_STSM/rx1/measurements/rx1_video_2023-03-15_03-13-23_exposure_33333.h264")

    while True:
        starttime = timeit.default_timer()
        good_frame, frame = cap.read()
        if not good_frame:  # if I got a bad frame, I shutdown
            print("ERROR: NO FRAME")
            pipe.send(PROCESS_SHUTDOWN)
            break

        msg = pipe.recv()  # checks at what state the algorithm process is at right now (busy or ready)
        if msg == PROCESS_READY:
            pipe.send(frame)
        if msg == PROCESS_BUSY:
            good, frame = cap.read()
        timeend = timeit.default_timer()
        timepass = (int((timeend - starttime) * 1000)) / 1000
        #print(timepass)
    cap.release()
    cv2.destroyAllWindows()


def AlgorithmProcess(pipe, mainPipe):
    
    
    
    # Decoding/DSP (digital signal processing) parameters
    buffer_size = 150
    signal_buff = collections.deque(maxlen = buffer_size)
    signal_buff.extend(np.zeros(buffer_size))
    signal_x = np.linspace(0,buffer_size, buffer_size) #fix this
    signal_y = np.array(signal_buff)
    

    extinction_ratio = 0.5
    
    bg_level = np.min(signal_y)
    one_level = np.max(signal_y)
    threshold = int((bg_level+one_level)*extinction_ratio)
    
    q = 4 #decimation factor
    
    #initialize figure
    fig = plt.figure(1,(5,5),96)
    plt.ion()
    ax = fig.add_subplot(111)
    line1, = ax.plot(signal_x,signal_y,'.-')
    #line2, = ax.plot(decimate(signal_x,q),decimate(signal_y,q),'o-')
    bg_line = ax.axhline(y = bg_level, color = 'k', linestyle = '--')
    thr_line = ax.axhline(y = threshold, color = 'b', linestyle = '--')
    one_line = ax.axhline(y = one_level, color = 'k', linestyle = '--')
    plt.ylabel("Selected pixel intensity")
    plt.xlabel("Sampling window ()")
    ax.set_ylim(0,255)
    plt.show()
    
    buffer_counter = 0
    
    message = ' '
    global mouse_x,mouse_y
    mouse_x = 100
    mouse_y = 100
    
    
    while True:
        
        starttime = timeit.default_timer()
        # receiving the frames
        pipe.send(PROCESS_READY)  # sending that i'm ready to receive a frame
        frame = pipe.recv()  # receiving the frame (MP library blocks (freezes) the code until it receives a frame, bear in mind)
        if frame == PROCESS_SHUTDOWN:  # checks if the Camera Process sent a shutdown request
            mainPipe.send(PROCESS_SHUTDOWN)
            break
        pipe.send(PROCESS_BUSY)  # sending that I'm busy from now on, so the camera process will empty the buffer.

        rows, cols, _ = np.shape(frame)  # reads the size of the frame

        """
        ---------------------------------------------
        >> All your computer vision algorithm here <<
        ---------------------------------------------
        """

        # mouse_x = int(frame.shape[1]/2)
        # mouse_y = int(frame.shape[0]/2)
        x = mouse_x
        y = mouse_y
        
        
        #px_val = int(np.average(frame[x,y,:]))
        px_val = int((frame[mouse_y,mouse_x,0]))
        signal_buff.append(px_val)
        buffer_counter +=1
        signal_y = np.array(signal_buff)
        line1.set_ydata(signal_y)
        #line2.set_ydata(decoded_signal*255)
        #bg_line.set_ydata(bg_level)
        #thr_line.set_ydata(threshold)
        #one_line.set_ydata(one_level)
        
        fig.canvas.draw()
        fig.canvas.flush_events()

        #cv2.line(frame, (0,x), (frame.shape[0],x), (0, 255, 0))
        cv2.line(frame, (x,0), (x,frame.shape[0]), (0, 255, 0))
        #cv2.line(frame, (y,0), (y,int(frame.shape[1])), (0, 255, 0))
        cv2.line(frame, (0,y), (int(frame.shape[1]),y), (0, 255, 0))
        
        if buffer_counter >= buffer_size:
            """
            DECODING PROCESS
            """
            
            
            
            y_downsamp = decimate(signal_y,4)
            
            
            bg_level = np.min(signal_y)
            one_level = np.max(signal_y)
            threshold = int((bg_level+one_level)*extinction_ratio)
            full_threshold = (signal_y > threshold)
    
            edges = np.argwhere(np.diff(full_threshold))[1:-1]
            bit = full_threshold[0]
    
            decoded_signal = bit
            decoded_signal_size = 1
    
            for i in range(len(edges)-1):
                array = np.array([0,4, 8, 12, 16, 20])
                pulse_samples_qty = edges[i+1]-edges[i]
                pulse_bit_qty = (np.abs(array - pulse_samples_qty)).argmin()
                for j in range(pulse_bit_qty):
                    decoded_signal = np.append(decoded_signal,bit)
                    decoded_signal_size += 1
                bit = not bit
    
            #decoded_signal = (y_downsamp > threshold)#[::4]#in previous version you would resample with this numeric tool
            detected_packet = np.zeros(15).astype(int)
            character=' '
            payload=np.zeros(8).astype(int)
            for i in range(decoded_signal_size-15):
                if decoded_signal[i] and decoded_signal[i+1] and decoded_signal[i+2] and decoded_signal[i+3] and decoded_signal[i+4] and not(decoded_signal[i+5]) and not(decoded_signal[i+10]):
                    detected_packet = decoded_signal[i:i+15]
                    payload = detected_packet[[6,7,8,9,11,12,13,14]]
                    character = chr(np.packbits(payload).tolist()[0])
                    if character != message[-1]:
                        if character == 'M':
                            message = " "
                        message += character
                    print("packet detected: {}, payload {}, char:{}".format(detected_packet.astype(int),payload.astype(int),character))
                    #print(signal_buff)
                    break
                else:
                    detected_packet = np.zeros(15)
                    payload = np.zeros(8)
                    character = ''
                
            
            #Detect packet header
            
            
            
        
        
        """
        DISPLAY RESULTS
        """
        
        
        #print(signal)
        
        #cv2.putText(frame, "Pixel value: {}".format(np.array(signal_buff)), (int(rows * 0.025), int(cols * 0.025)), font, 0.5, (0, 255, 0),1, cv2.LINE_AA)
        #push pixel value into 
        

        """
        ---------------------------
        >> End of your algorithm <<
        ---------------------------
        """
        timeend = timeit.default_timer()
        timepass = (int((timeend - starttime) * 1000)) / 1000
        # print all this very interesting stuff
        #if buffer_counter >= buffer_size:
            #cv2.putText(frame, "packet detected: {}, payload: {}, char: {}".format(detected_packet.astype(int),payload.astype(int),character), (int(rows * 0.025), int(cols * 0.025)), font, 0.3, (0, 255, 0),1, cv2.LINE_AA)
        cv2.putText(frame, message, (int(rows * 0.025), int(cols * 0.075)), font, 2, (0, 255, 0),1, cv2.LINE_AA)
        cv2.imshow("Camera", frame)
        cv2.setMouseCallback("Camera",define_xy)
        if cv2.waitKey(1) & 0xFF == 27:  # press ESC to exit
            mainPipe.send(PROCESS_SHUTDOWN)
            print("Algorithm Processor: EXIT REQUEST")


if __name__ == "__main__":
    AlgorithmSide, CameraSide = multiprocessing.Pipe()  # creates two sided pipe from algorithm to camera
    MainSide, AlgorithmToMainSide = multiprocessing.Pipe()  # creates a two sided pipe from main to algorithm
    p1 = multiprocessing.Process(target=CameraProcess, args=(AlgorithmSide,))  # creates the camera process
    p2 = multiprocessing.Process(target=AlgorithmProcess, args=(CameraSide, AlgorithmToMainSide))  # creates the algorithm process
    p1.start()  # obviously..
    p2.start()
    while True:  # loops main process to see if i'm ready to shutdown
        if MainSide.recv() == PROCESS_SHUTDOWN:
            print("Main Process: EXIT REQUEST")
            break
    p1.terminate()  # obviously
    print("Camera Process Terminated")
    p2.terminate()
    print("Algorithm Process Terminated")

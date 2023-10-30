#!/usr/bin/env python3
import api
import requests
import threading
import time 
import datetime

global power
global current
global countdown

global tasmotaip
tasmotaip = "192.168.1.9" # the IP address of your tasmota-enabled smart plug. Should be a fixed address though.

countdown = 10 #seconds to count down in the thread before we verify the standby; e.g. 5*60 are 5 Minutes
global check_delay
check_delay = 30 #seconds between two pollings

global standby
standby = False
global event
global thread


def timer(event):
    global standby
    global countdown
    
    while not event.isSet() and countdown > 0:
       print("timer running... "+ str(countdown)) 
       countdown =  countdown -1
       event.wait(1)
       if standby == False:
            print("aborting timer at "+str(datetime.datetime.now()))
            event.set()

    if standby == True:
        print ("stopping timer at "+str(datetime.datetime.now()))
        event.set() #stop timer from executing
    elif standby == False:
        print("aborting timer at "+str(datetime.datetime.now()))
        event.set() 

def get_values_from_tasmota():
    global power
    global current
    try:
        response = requests.get("http://"+tasmotaip+"/cm?cmnd=status%208")
        data = response.json()
    except:
        print("tasmota not online")
        exit(0)
    
    #print(type(data))
    #print(data['StatusSNS']['ENERGY']['Power'])
    power = data['StatusSNS']['ENERGY']['Power']
    # power is about 71-80 while TV is on, blank screen is about 60, in standby it is about 14 W
    # current is about 0.34-0.37 while TV is on, blank screen 0.298, about 0.119 in standby
    current = data['StatusSNS']['ENERGY']['Current']
    #print(type (power))
    #print(type (current))
    print ("power is {:2d} W".format(power)+" at " +str(datetime.datetime.now()))

def toggle_switchbot():
    global standby
    api.make_header()
    apiHeader=api.apiHeader
    apiBody={}
    apiBody['commandType']='command'
    apiBody['command']='press'
    apiBody['parameter']='default'
    deviceid='C5154D75B528' # TV Schalter Bot
    if standby == True:
       #url="https://api.switch-bot.com/v1.1/devices/"+deviceid+"/status"
       #response=requests.get(url,headers=apiHeader).json()
       
       url="https://api.switch-bot.com/v1.1/devices/"+deviceid+"/commands"
       response=requests.post(url,headers=apiHeader,json=apiBody)
       print("status code:{}",response.status_code)
       response_json=response.json() # jsons are tuples, too
       print(response_json)
       time.sleep(10)
       if response_json['message'] == 'success':
            stop_timer()


def stop_timer():
    global thread
    if thread.is_alive() == True:
        print ("Thread is alive")
    else:
        print ("Thread is dead")
    global event
    event.clear()
    global standby
    standby=False
    print("timer stopped at "+str(datetime.datetime.now()))

def start_timer():
    global event
    global thread
    event=threading.Event()
    thread = threading.Thread(target=timer, args=(event,))
    thread.start()
    print("timer started at "+str(datetime.datetime.now()))

last_power =0 #we do not know what happened before we were running this python script

while (1):
    get_values_from_tasmota()
    #debug prints
    #print('power='+str(power))
    #print('current='+str(current))
    print ("last_power was {:d} W".format(last_power))
    if power > 55 : # it is usually 60-80 W, sometimes about 47W
        print ('{:2d} W: TV is on'.format(power))
        
        standby=False
    elif power > 10 and power < 30: #in standby, it is about 14 W
        print ("{:2d} W: TV is in standby".format(power))
        #great, but now check if we were in standby before, to avoid false positives while powering the TV on
        if last_power > 10 and last_power < 50:
            print ("{:2d} W: TV was in standby for at least {:d} seconds".format(last_power,check_delay))
            if standby == False: # so we did turn the status off but the switching off is still going on
                standby=True
                try: 
                    if event in vars() or event in globals() or event in locals():
                        if event.is_set():
                            event.clear()
                except NameError:
                    print ("event object was not set yet")
                    pass

            start_timer() #just for the output.
            time.sleep(countdown)
            if standby == True:
                print("toggle_switchbot()")
                toggle_switchbot()
                stop_timer()
            

    elif power < 1:
        print ("{:2d} W: TV is off".format(power))
        standby=False
    
    else:
        print("{:d} W, {:f} A: something is wrong".format(power,current))

    time.sleep(check_delay) #check only every n seconds
    last_power = power

#eof

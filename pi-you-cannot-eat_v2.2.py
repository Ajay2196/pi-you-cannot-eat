# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple test for NeoPixels on Raspberry Pi
import time
import board
import neopixel
import datetime
import requests
import math
from gpiozero import Button
from signal import pause
import dateutil
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 12
isMapped=False;
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB
isMapped = False;
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER
)

button = Button(2)

class Item():
    def __init__(self):
        self.label = None
        self.index = None
        self.expiry= None
        self.status= "Green"

blink = False    
Items = []

def showLight(item,index):
    time.sleep(1);
    current_date = datetime.datetime.today()
    days_left = (item.expiry - current_date).days

    if days_left >= 3:
        print(days_left)
        print(item.label+" Green", days_left)
        pixels[item.index] =  (0,128,0)
        
    elif days_left <= 2 and days_left >= 0:
        print(item.label+" Orange")
        Items[index].status="Orange"
        pixels[item.index] =  (255,140,0)
    
    else:
        print(item.label+" Red")
        Items[index].status="Red"
        pixels[item.index] =  (255,0,0)
        
    pixels.show()
#     pixelObj.show()




        
# pair request
pairparams = dict(
    deviceID='Pi008')
user = object();
userID = '';
isPaired = False;

def getPairing():
    global user;
    global isPaired;
    global userID;
    global  isMapped;
    user = requests.get('https://iot-pi-you-cannot-eat.herokuapp.com/piConfig/pairRequest',params=pairparams).json()['pairData'];
    if(isPaired == False and len(user)>0):
        spinner(0.01);
        clearPixels();
        isPaired = True
        userID=user[0]['userId'];
        mapItems();
    if(isPaired == True and len(user)==0):
        print("unpaired");
        isPaired = False;
        clearPixels();
        spinner(0.01);
        clearPixels();
    

    
    
def mapItems():
    global isMapped;
    params = dict(
        id= userID)
    initData = requests.get('https://iot-pi-you-cannot-eat.herokuapp.com/piConfig/getAllConfig',params=params);
    print(initData.json());
    itemsToBeMapped = initData.json()['items'];
    totalItemsMapped= len(itemsToBeMapped);
    global Items;
    Items = [];
    print(itemsToBeMapped);
    for x in range(totalItemsMapped):
        Items.append(Item())
        print(itemsToBeMapped[x]['label'], itemsToBeMapped[x]['index'], itemsToBeMapped[x]['expiry'])
        Items[x].label = itemsToBeMapped[x]['label'];
        Items[x].index = itemsToBeMapped[x]['index'];
        Items[x].expiry = datetime.datetime.strptime(itemsToBeMapped[x]['expiry'], "%Y-%m-%dT%H:%M:%S.%fZ");
        showLight(Items[x],x);
    isMapped = True;
    print(isMapped,"from MapItems");



def blinkLight(index):
    global blink;
    while (blink==True):
        print(blink)
        pixels[index] = (255,0,0);
        pixels.show();
        time.sleep(1);
        pixels[index] = (0,0,0);
        pixels.show();
        time.sleep(1);
        button.when_pressed = blinkOff
    mapItems();
    
def spinner(wait,indefinite=False):
    if(indefinite==True):
        cycles = 0 
        while cycles <=7:
            for j in range(255):
                for i in range(num_pixels):
                    pixel_index = (i * 256 // num_pixels) + j
                    pixels[i] = wheel(pixel_index & 255)
                pixels.show()
                time.sleep(wait);
                cycles=cycles+wait;
    else:
         for j in range(255):
                for i in range(num_pixels):
                    pixel_index = (i * 256 // num_pixels) + j
                    pixels[i] = wheel(pixel_index & 255)
                pixels.show()
                time.sleep(wait);
                
        
            
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)



def blinkOff():
    global blink;
    blink = False;
    
def getNotif():
    global blink;
    userID=user[0]['userId'];
    params = dict(
    userID = userID);
    notification = requests.get('https://iot-pi-you-cannot-eat.herokuapp.com/piUpdates/getNewUpdate',params=params);
    notification = notification.json();
    print(notification);
    if(notification['hasUpdate'] == True and notification['isDeleted'] != True):
        blink = True;
        blinkLight(notification['ledID']);
        deleteNotification = requests.delete('https://iot-pi-you-cannot-eat.herokuapp.com/piUpdates/deleteUpdate',params=params);
    
#     elif(notification['hasUpdate'] == True and notification['isDeleted']== True):
#         deletedIndex=notification['ledID'];
#         pixels[deletedIndex]=(0,0,0);
#         deleteNotification = requests.delete('https://iot-pi-you-cannot-eat.herokuapp.com/piUpdates/deleteUpdate',params=params);
#         mapItems();
#     else:
#         return;
    
def sendData():
    if(isPaired == False):
        return;
    to_be_notified =[]
#     removeItem()
    for item in Items:
     if item.status != "Green":
         to_be_notified.append(item.label+" status :"+item.status)
    print(to_be_notified)
    myobj = {'user': user[0]['user'],
              'item':to_be_notified}
    postNotification = requests.post('https://iot-pi-you-cannot-eat.herokuapp.com/pi/addNotification',json = myobj)
#     print(postNotification.json())
#


#
def clearPixels():
    global Items;
    Items = [];
    pixels.fill((0,0,0))
    pixels.show();
# blinkLight(0);
clearPixels();
spinner(0.02,True);
clearPixels();
while True:
#     time.sleep(1)
    getPairing();
    for x,item in enumerate(Items):
        showLight(Items[x],x);
        pixels.show();
    if(isPaired == True):
        getNotif();
    button.when_pressed = sendData;
#     RED = 0x100000 # (0x10, 0, 0)
#     GREEN = 0x001000
#     BLUE = 0x000010
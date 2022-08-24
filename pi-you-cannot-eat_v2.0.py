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

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
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
    deviceID='Pi007')
user = object();
userID = '';
def getPairing():
    global user;
    global userID;
    user = requests.get('https://iot-pi-you-cannot-eat.herokuapp.com/piConfig/pairRequest',params=pairparams).json()['pairData'];
    userID=user[0]['userId'];

def mapItems():
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



def blinkLight(index):
    global blink;
    blink = True;
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
    
        
        
def blinkOff():
    global blink;
    blink = False;
    
def getNotif():
    userID=user[0]['userId'];
    params = dict(
    userID = userID);
    notification = requests.get('https://iot-pi-you-cannot-eat.herokuapp.com/piUpdates/getNewUpdate',params=params);
    notification = notification.json();
    print(notification);
    if(notification['hasUpdate'] == True and notification['isDeleted'] != True):
        blinkLight(notification['ledID']);
        deleteNotification = requests.delete('https://iot-pi-you-cannot-eat.herokuapp.com/piUpdates/deleteUpdate',params=params);
    
    elif(notification['hasUpdate'] == True and notification['isDeleted']== True):
        deletedIndex=notification['ledID'];
        pixels[deletedIndex]=(0,0,0);
        deleteNotification = requests.delete('https://iot-pi-you-cannot-eat.herokuapp.com/piUpdates/deleteUpdate',params=params);
        mapItems();
    else:
        return;
    
def sendData():
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
    
time.sleep(10);
getPairing();
mapItems();
   
pixels.fill((0,0,0))
# blinkLight(0);
while True:
    time.sleep(1)
    for x,item in enumerate(Items):
        showLight(Items[x],x)
        pixels.show();
    getNotif();
    button.when_pressed = sendData;
#     RED = 0x100000 # (0x10, 0, 0)
#     GREEN = 0x001000
#     BLUE = 0x000010


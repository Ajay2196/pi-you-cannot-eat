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
#     pixelObj.show()



class Item():
    def __init__(self):
        self.label = None
        self.index = None
        self.expiry= None
        self.status= "Green"
        
Items = []
for x in range(6):
    Items.append(Item())
# Initialization    
Items[0].label = "food Item A"
Items[0].index = 0
Items[0].expiry = datetime.datetime(2022,7,10)
Items[1].label = "food Item B"
Items[1].index = 2
Items[1].expiry = datetime.datetime(2022,7,3)
Items[2].label = "food Item C"
Items[2].index = 4
Items[2].expiry = datetime.datetime(2022,7,6)
Items[3].label = "food Item D"
Items[3].index = 6
Items[3].expiry = datetime.datetime(2022,7,8)
Items[4].label = "food Item E"
Items[4].index = 8
Items[4].expiry = datetime.datetime(2022,7,10)
Items[5].label = "food Item F"
Items[5].index = 10
Items[5].expiry = datetime.datetime(2022,7,12)

def sendData():
    to_be_notified =[]
#     removeItem()
    for item in Items:
     if item.status != "Green":
         to_be_notified.append(item.label+" status :"+item.status)
    print(to_be_notified)
    myobj = {'user':'AJ',
              'item':to_be_notified}
    postNotification = requests.post('https://iot-pi-you-cannot-eat.herokuapp.com/pi/addNotification',json = myobj)
#     print(postNotification.json())
    
def removeItem():
    reqObj = {'user' : "AJ"}
    getRemoveItemsFromServer = requests.get('https://iot-pi-you-cannot-eat.herokuapp.com/pi/updatedLED',data = reqObj)
    print(getRemoveItemsFromServer.content)
#     for index,item in enumerate(Items):
#         if item.index==ind:
#             Items.remove(Items[index]);
            
   

pixels.fill((0,0,0))
while True:
    # Comment this line out if you have RGBW/GRBW NeoPixels
    time.sleep(1)
    for x,item in enumerate(Items):
        showLight(Items[x],x)
    
    pixels.show()
    
    button.when_pressed = sendData
    
#     RED = 0x100000 # (0x10, 0, 0)
#     GREEN = 0x001000
#     BLUE = 0x000010
    
    
   
        
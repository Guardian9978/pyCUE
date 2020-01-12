This is how you use this possibly useful API.
```python
#first we import the main class
from pyCUE_api.pyCUE_api import Controller

#We setup our dll handler
#This function takes an optional parameter of True. (If not specified it defaults to False)
#This paramater is used to determin if this program is going to take exclusive control of your led controller.
handle = Controller()

#NOTE: Device IDs count up from 0 so if you only have 1 device your Device ID would be 0.

#To get the amount of devices detected
count = handle.deviceGetCount() #(Returns an Integer)

#We can then get the led count
count = handle.ledGetCount(deviceid) #(Paramaters taken Integer | Returns an Integer)
count = handle.ledGetCount() #For Keyboards: (Returns an Integer) 

#Get the current LED color using a Device ID. (Paramaters taken int DeviceID | Returns an Array)
array = handle.ledGetColor(deviceid, 200)
red = array[0].r #red
green = array[0].g #green
blue = array[0].b #blue

#Get the current LED color using a Device ID. (Paramaters taken int DeviceID, int list ledids | Returns an Array)
array = handle.ledGetColor(deviceid, [200,201])
led1_red = array[0].r   #LED 1 Red
led1_green = array[0].g #LED 1 Green
led1_blue = array[0].b  #LED 1 Blue
led2_red = array[1].r   #LED 2 Red
led2_green = array[1].g #LED 2 Green
led2_blue = array[1].b  #LED 2 Blue

#Set an led to a color
#Paramaters taken int Device ID, int Led ID, List of Red, Green, and Blue, EXAMPLE: [Red, Green, Blue]
handle.ledSetColor(deviceid, ledid, [0, 255, 0]) # Set the Led ID specifed to the color Green
handle.flush() #Makes the change apear on the Led
```

EXAMPLE:
```python
from pyCUE_api.pyCUE_api import Controller

handle = Controller()

count = handle.deviceGetCount()
print("Devices Found: " + str(count))

count = handle.ledGetCount(0)
print("Leds found on Device 0: " + str(count))

array = handle.ledGetColor(0, 200)
r = array[0].r
g = array[0].g
b = array[0].b
print("LED 200 on Device 0 Color: [" + str(r) + ", " + str(g) + ", " + str(b) + "]")

handle.ledSet(0, 200, [0, 0, 255])
handle.flush()
print("Set LED 200 on Device 0 to Blue")
```

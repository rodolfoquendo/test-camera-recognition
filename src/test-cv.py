import cv2
import json
import keyboard
import numpy as np
import os.path
import pyaudio
configs = {
    "window_name" : "test",
    "video" : {
        "FPS" : 23
    },
    "transformations" : {
        "grayscale" : True,
        "comic" : False,
    },
    "classifiers" : {
        "full_body" : {
            "enabled" : True,
            "legend" : True,
            "model" : "haarcascade_fullbody",
        },
        "face" : {
            "enabled" : True,
            "legend" : True,
            "model" : "haarcascade_frontalface_default",
        },
        "eyes" : {
            "enabled" : False,
            "legend" : True,
            "model" : "haarcascade_eye",
        },
        "glasses" : {
            "enabled" : True,
            "legend" : True,
            "model" : "haarcascade_eye_tree_eyeglasses",
        },
        "smile" : {
            "enabled" : False,
            "legend" : True,
            "model" : "haarcascade_smile",
        },
    }
}
def nothing(x):
    pass

__PATH_CURRENT_CAMERA__ = "./.current_camera"
__CACHE_DEVICE_LIST__ = "./.available_devices"
def updateCurrentCamera(camera_id):
    file = open(__PATH_CURRENT_CAMERA__, "w")
    file.write(str(camera_id))
    file.close()
def getCurrentCamera():
    file = open(__PATH_CURRENT_CAMERA__, "r")
    return int(file.read())
def switchCamera():
    current = getCurrentCamera()
    devices = getAvailableDevices()
    devices = devices["video"]
    for device in devices:
        if(device["camera_index"] > current):
            updateCurrentCamera(device["camera_index"])
            return getCurrentCamera()
    updateCurrentCamera(0)
    return 0


def videoDevices() :
    from rodolfoquendo.Services.Media.VideoCapture import VideoCapture
    service = VideoCapture()
    return service.getDevices()

def audioDevices() :
    devices = {}
    pyduo = pyaudio.PyAudio()
    devices_info = pyduo.get_host_api_info_by_index(0)
    for device_index in range(0, devices_info.get('deviceCount')):
        if (pyduo.get_device_info_by_host_api_device_index(0, device_index).get('maxInputChannels')) > 0:
            devices[device_index] = pyduo.get_device_info_by_host_api_device_index(0, device_index).get('name')
    return devices


def getAvailableDevices():
    if not os.path.exists(__CACHE_DEVICE_LIST__):
        devices = {
            "video" : videoDevices(),
            "audio" : audioDevices(),
        }
        print(devices,json.dumps(devices))
        file = open(__CACHE_DEVICE_LIST__, "w")
        file.write(json.dumps(devices))
        file.close()
    
    file = open(__CACHE_DEVICE_LIST__, "r")
    return json.loads(file.read())

devices = getAvailableDevices()

classifiers = {}
for classifier in configs["classifiers"].keys():
    if (configs["classifiers"][classifier]["enabled"]) :
        classifiers[classifier] = cv2.CascadeClassifier(
            cv2.data.haarcascades + configs["classifiers"][classifier]["model"] + ".xml"
        )

cv2.namedWindow(configs['window_name'])
# cv2.createButton("Camera switch",nothing)
print("current device" , getCurrentCamera(), getAvailableDevices())

def initCapture():
    vc = cv2.VideoCapture(getCurrentCamera())
    vc.set(cv2.CAP_PROP_FPS, configs['video']['FPS'])
    return vc
vc = initCapture()
if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    # reading the frame
    rval, frame = vc.read()
    # manipulate the frame
    # turn it to grayscale
    if(configs['transformations']['grayscale']):
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # make it comic
    if(configs['transformations']['comic']):
        ret,frame = cv2.threshold(frame,80,255,cv2.THRESH_BINARY)

    for classifier in classifiers.keys():
        instance = classifiers[classifier]
        item = instance.detectMultiScale(
            frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        for (x, y, w, h) in item:
            image = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv2.putText(image, classifier, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

    # displaying the frame
    cv2.imshow(configs['window_name'], frame)
    # key to end everything
    key = cv2.waitKey(20)
    if key == 27: # esc
        break
    elif key == 32: # space
        oldDevice = getCurrentCamera()
        newDevice = switchCamera()
        print("switch", oldDevice, newDevice)
        vc.release()
        vc = initCapture()

cv2.destroyWindow(configs['window_name'])
    
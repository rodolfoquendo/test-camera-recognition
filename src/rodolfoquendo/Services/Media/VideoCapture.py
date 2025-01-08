import asyncio
import platform
import subprocess
import os
import cv2

if platform.system() == 'Windows':
    import winrt.windows.devices.enumeration as windows_devices

VIDEO_DEVICES = 4

class VideoCapture:
    max_numbers_of_cameras_to_check = 10
    def __init__(self):
        self.devices = []

    def getDevices(self) -> list:
        self.devices = []
        camera_indexes = self.getDeviceIndexes()
        if len(camera_indexes) == 0:
            return self.devices
        self.devices = self.getDeviceInformation(camera_indexes)
        return self.devices

    def getDeviceIndexes(self):
        index = 0
        camera_indexes = []
        max_numbers_of_cameras_to_check = self.max_numbers_of_cameras_to_check
        while max_numbers_of_cameras_to_check > 0:
            try:
                capture = cv2.VideoCapture(index)
                if capture.read()[0]:
                    camera_indexes.append(index)
                    capture.release()
            except Exception:
                pass
            index += 1
            max_numbers_of_cameras_to_check -= 1
        return camera_indexes

    def getWindowsInformation(self, camera_indexes):
        cameras = []
        cameras_info_windows = asyncio.run(self.get_camera_information_for_windows())
        for camera_index in camera_indexes:
            camera_name = cameras_info_windows.get_at(camera_index).name.replace('\n', '')
            cameras.append({'camera_index': camera_index, 'camera_name': camera_name})
        return cameras

    def getMacInformation(self, camera_indexes):
        devices = subprocess.run(['system_profiler','SPCameraDataType',' |grep "Model ID:"'],stdout=subprocess.PIPE).stdout.decode('utf-8')
        devices = devices.split("\n")
        _devices = []
        cameras = []
        for device in devices:
            needle = "Model ID: "
            if needle in device:
                _devices.append(device[device.find(needle) + len(needle):])
        for camera_index in camera_indexes:
            cameras.append({'camera_index': camera_index, 'camera_name': _devices[camera_index]})
        return cameras

    def getLinuxInformation(self, camera_indexes):
        cameras = []
        for camera_index in camera_indexes:
            camera_name = subprocess.run(['cat', '/sys/class/video4linux/video{}/name'.format(camera_index)],
                                            stdout=subprocess.PIPE).stdout.decode('utf-8')
            camera_name = camera_name.replace('\n', '')
            cameras.append({'camera_index': camera_index, 'camera_name': camera_name})
        return cameras

    def getDeviceInformation(self, camera_indexes: list) -> list:
        platform_name = platform.system()
        if platform_name == 'Windows':
            return self.getWindowsInformation(camera_indexes=camera_indexes)

        if platform_name == 'Darwin':
            return self.getMacInformation(camera_indexes=camera_indexes)
            
        if platform_name == 'Linux':
            return self.getLinuxInformation(camera_indexes=camera_indexes)

    async def get_camera_information_for_windows(self):
        return await windows_devices.DeviceInformation.find_all_async(VIDEO_DEVICES)


camera = VideoCapture()
print(camera.getDevices())
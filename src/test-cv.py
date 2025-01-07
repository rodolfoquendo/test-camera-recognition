import numpy as np
import cv2
window_name = 'Test Rodolfo'
cv2.namedWindow(window_name)

vc = cv2.VideoCapture(0)


hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eyes_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

glasses_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml"
)
smiles_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_smile.xml"
)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    # reading the frame
    rval, frame = vc.read()
    # manipulate the frame
    # turn it to grayscale
    # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # make it comic
    # ret,frame = cv2.threshold(frame,80,255,cv2.THRESH_BINARY)
    # detect the face
    face = face_classifier.detectMultiScale(
        frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )
    glasses = glasses_classifier.detectMultiScale(
        frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )
    eyes = eyes_classifier.detectMultiScale(
        frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )
    smile = smiles_classifier.detectMultiScale(
        frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )
    # circle up the face
    for (x, y, w, h) in face:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    # circle up the face
    for (x, y, w, h) in glasses:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    # circle up the face
    for (x, y, w, h) in eyes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    # circle up the face
    # for (x, y, w, h) in smile:
    #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
     # detect people in the image
    # returns the bounding boxes for the detected objects
    boxes, weights = hog.detectMultiScale(frame, winStride=(8,8) )

    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

    for (xA, yA, xB, yB) in boxes:
        # display the detected boxes in the colour picture
        cv2.rectangle(frame, (xA, yA), (xB, yB),(0, 255, 0), 2)
    

    # displaying the frame
    cv2.imshow(window_name, frame)
    # key to end everything
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

vc.release()
cv2.destroyWindow(window_name)
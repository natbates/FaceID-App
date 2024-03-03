import cv2
import numpy as np
from PIL import Image
import os


def train():
    # Directory path where the face images are stored.
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    path = "images"
    # Haar cascade file for face detection
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def getImagesAndLabels(path):

        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []
        for imagePath in imagePaths:
            # Convert image to grayscale
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            # Extract the user ID from the image file name
            # Detect faces in the grayscale image
            faces= detector.detectMultiScale(img_numpy)
            id = int(os.path.split(imagePath)[-1].split(".")[0])

            for (x, y, w, h) in faces:
                # Extract face region and append to the samples
                faceSamples.append(img_numpy[y:y+h, x:x+w])
                ids.append(id)

        return faceSamples, ids

    faces, ids= getImagesAndLabels(path)
    if len(ids) > 0:
        recognizer.train(faces, np.array(ids))
    
    # Save the trained model into the current directory
        recognizer.write('trainer.yml')
    
    #print("\n[INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))

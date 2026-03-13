from PIL import Image
import numpy as np
import face_recognition

img = Image.open("pre_registered/photos/image.jpg").convert('RGB')
arr = np.array(img)
print(arr.shape, arr.dtype)
encodings = face_recognition.face_encodings(arr)
print("Encodings found:", len(encodings))

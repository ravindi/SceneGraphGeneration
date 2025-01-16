from ultralytics import YOLO
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import cv2

model = YOLO("yolov8n.pt")
response = requests.get("https://qrfirm.com/wp-content/uploads/2021/02/shutterstock_1055845817-scaled.jpg")
image = Image.open(BytesIO(response.content))
image = np.asarray(image)
results = model.predict(image)

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QMessageBox, QLabel, QFileDialog
from rdflib import Graph, RDF, URIRef, OWL, Namespace
import re
import numpy as np
from PIL import Image
from io import BytesIO
import cv2
from ultralytics import YOLO
from PyQt5.QtGui import QPixmap


def box_label(image, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
    lw = max(round(sum(image.shape) / 2 * 0.003), 2)
    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
    cv2.rectangle(image, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)
    if label:
        tf = max(lw - 1, 1)  # font thickness
        w, h = cv2.getTextSize(label, 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
        outside = p1[1] - h >= 3
        p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
        cv2.rectangle(image, p1, p2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(image,
                    label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                    0,
                    lw / 3,
                    txt_color,
                    thickness=tf,
                    lineType=cv2.LINE_AA)


class DetectObjects(QMainWindow):
    MY_NS = Namespace("http://www.semanticweb.org/ardesilva/KnowledgeGraph#")

    def __init__(self):
        super().__init__()

        self.initUI()
        self.init_graph()
        self.model = None

    def initUI(self):
        # Set up the main window
        self.setWindowTitle("Ontology Scene Description")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Scene description input
        self.scene_description_input = QTextEdit(self)
        layout.addWidget(self.scene_description_input)

        # Upload image button
        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_button)

        # Label to display uploaded image
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # Label to display detected objects
        self.detected_objects_label = QLabel("Detected Objects:", self)
        layout.addWidget(self.detected_objects_label)

    def init_graph(self):
        # Initialize the RDF Graph
        self.g = Graph()
        self.g.parse("ravdKGMerged1.owl")

    def upload_image(self):
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png *.bmp)")
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                pixmap = QPixmap(file_path)
                self.image_label.setPixmap(pixmap)
                # Call object detection function
                self.run_object_detection(file_path)
        except Exception as e:
            print("Error uploading image:", e)

    def run_object_detection(self, image_path):
        if self.model is None:
            self.model = YOLO("yolov8n.pt")

        try:
            image = Image.open(image_path)
            # Convert the PIL image to a NumPy array
            image_np = np.array(image)
            # Convert the NumPy array to integers
            image_np_int = image_np.astype(int)
            results = self.model.predict(image_np_int)
            print(results[0].boxes.data)
            self.plot_bboxes(image_np_int, results[0].boxes.data, conf=0.6)

        except Exception as e:
            print("Error during object detection:", e)

    def plot_bboxes(image, boxes, labels=[], colors=[], score=True, conf=None):
        if labels == []:
            # Define COCO Labels
            labels = {0: u'__background__', 1: u'person', 2: u'bicycle', 3: u'car', 4: u'motorcycle', 5: u'airplane', 6: u'bus', 7: u'train', 8: u'truck', 9: u'boat', 10: u'traffic light', 11: u'fire hydrant', 12: u'stop sign', 13: u'parking meter', 14: u'bench', 15: u'bird', 16: u'cat', 17: u'dog', 18: u'horse', 19: u'sheep', 20: u'cow', 21: u'elephant', 22: u'bear', 23: u'zebra', 24: u'giraffe', 25: u'backpack', 26: u'umbrella', 27: u'handbag', 28: u'tie', 29: u'suitcase', 30: u'frisbee', 31: u'skis', 32: u'snowboard', 33: u'sports ball', 34: u'kite', 35: u'baseball bat', 36: u'baseball glove', 37: u'skateboard', 38: u'surfboard', 39: u'tennis racket', 40: u'bottle', 41: u'wine glass', 42: u'cup', 43: u'fork', 44: u'knife', 45: u'spoon', 46: u'bowl', 47: u'banana', 48: u'apple', 49: u'sandwich', 50: u'orange', 51: u'broccoli', 52: u'carrot', 53: u'hot dog', 54: u'pizza', 55: u'donut', 56: u'cake', 57: u'chair', 58: u'couch', 59: u'potted plant', 60: u'bed', 61: u'dining table', 62: u'toilet', 63: u'tv', 64: u'laptop', 65: u'mouse', 66: u'remote', 67: u'keyboard', 68: u'cell phone', 69: u'microwave', 70: u'oven', 71: u'toaster', 72: u'sink', 73: u'refrigerator', 74: u'book', 75: u'clock', 76: u'vase', 77: u'scissors', 78: u'teddy bear', 79: u'hair drier', 80: u'toothbrush'}

        if colors == []:
        # Define colors
            colors = [(89, 161, 197),(67, 161, 255),(19, 222, 24),(186, 55, 2),(167, 146, 11),(190, 76, 98),(130, 172, 179),(115, 209, 128),(204, 79, 135),(136, 126, 185),(209, 213, 45),(44, 52, 10),(101, 158, 121),(179, 124, 12),(25, 33, 189),(45, 115, 11),(73, 197, 184),(62, 225, 221),(32, 46, 52),(20, 165, 16),(54, 15, 57),(12, 150, 9),(10, 46, 99),(94, 89, 46),(48, 37, 106),(42, 10, 96),(7, 164, 128),(98, 213, 120),(40, 5, 219),(54, 25, 150),(251, 74, 172),(0, 236, 196),(21, 104, 190),(226, 74, 232),(120, 67, 25),(191, 106, 197),(8, 15, 134),(21, 2, 1),(142, 63, 109),(133, 148, 146),(187, 77, 253),(155, 22, 122),(218, 130, 77),(164, 102, 79),(43, 152, 125),(185, 124, 151),(95, 159, 238),(128, 89, 85),(228, 6, 60),(6, 41, 210),(11, 1, 133),(30, 96, 58),(230, 136, 109),(126, 45, 174),(164, 63, 165),(32, 111, 29),(232, 40, 70),(55, 31, 198),(148, 211, 129),(10, 186, 211),(181, 201, 94),(55, 35, 92),(129, 140, 233),(70, 250, 116),(61, 209, 152),(216, 21, 138),(100, 0, 176),(3, 42, 70),(151, 13, 44),(216, 102, 88),(125, 216, 93),(171, 236, 47),(253, 127, 103),(205, 137, 244),(193, 137, 224),(36, 152, 214),(17, 50, 238),(154, 165, 67),(114, 129, 60),(119, 24, 48),(73, 8, 110)]

        for box in boxes:
            if score:
                label = labels[int(box[-1]) + 1] + " " + str(round(100 * float(box[-2]), 1)) + "%"
            else:
                label = labels[int(box[-1]) + 1]

            if conf:
                if box[-2] > conf:
                    color = colors[int(box[-1])]
                    box_label(image, box, label, color)
            else:
                color = colors[int(box[-1])]
                box_label(image, box, label, color)

        return image

    def run_object_detection(self, image_path):
        if self.model is None:
            self.model = YOLO("yolov8n.pt")

        try:
            image = Image.open(image_path)
            image = np.array(image)
            # Perform object detection
            results = self.model.predict(image)
            print(results[0].boxes.data)
            image_with_boxes = self.plot_bboxes(image.copy(), results[0].boxes.data, conf=0.6)
            self.display_image(image_with_boxes)

        except Exception as e:
            print("Error during object detection:", e)

    def display_image(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Display the image in a window
        cv2.imshow("Detected Objects", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    app = QApplication([])
    window = DetectObjects()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
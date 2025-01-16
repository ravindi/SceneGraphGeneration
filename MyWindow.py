import uuid

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QMessageBox, \
    QLabel, QFileDialog, QComboBox, QListWidget
from rdflib import Graph, RDF, URIRef, OWL, Namespace, RDFS
import re
import numpy as np
from PIL import Image
from io import BytesIO
import cv2
from ultralytics import YOLO
from PyQt5.QtGui import QPixmap
import spacy
import random

class MyWindow(QMainWindow):
    MY_NS = Namespace("http://www.semanticweb.org/ardesilva/KnowledgeGraph#")
    TIME_NS = Namespace("http://www.w3.org/2006/time#")
    GEOSPATIAL_NS = Namespace("http://www.opengis.net/ont/geosparql#")

    def __init__(self):
        super().__init__()

        self.unique_subjects = []  # Define unique_subjects attribute
        self.initUI()
        self.init_graph()
        self.model = None
        self.current_step = 0
        self.model = None
        self.file_path = None
        self.existing_instances = {}  # Dictionary to store existing instances
        self.instances_created = {}
        self.bicycle_sensor_instances_created = set()
        self.vehicle_sensor_instances_created = set()

    # List all entities and relations in the ontology
        entities, relations = self.list_entities_and_relations()
        print("Entities:", entities)
        print("Relations:", relations)

    def create_instance(self, instance_uri, created_instance=None):
        # Your instance creation logic here
        self.instances_created[instance_uri] = created_instance
    
    def initUI(self):

        # Set up the main window
        self.setWindowTitle("Ontology Scene Description")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_button)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)
        self.image_label.hide()

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.next_step)
        layout.addWidget(self.next_button)
        self.next_button.hide()

        # Scene description input
        self.scene_description_input = QTextEdit(self)
        layout.addWidget(self.scene_description_input)
        self.scene_description_input.hide()

        # Process button
        self.process_button = QPushButton("Process Scene Description", self)
        self.process_button.clicked.connect(self.process_scene_description)
        layout.addWidget(self.process_button)
        self.process_button.hide()

    def init_graph(self):
        # Initialize the RDF Graph
        self.g = Graph()
        self.g.parse("ravdKGMerged1.owl")
        self.g.bind("my_ns", self.MY_NS)
        self.g.bind("time_ns", self.TIME_NS)
        self.g.bind("geospatial_ns", self.GEOSPATIAL_NS)

        # Extract and store subClassOf values
        self.subclass_of_map = {}
        for subclass_of in self.g.objects(predicate=RDFS.subClassOf):
            if subclass_of not in self.subclass_of_map:
                self.subclass_of_map[subclass_of] = []
            for class_uri in self.g.subjects(RDFS.subClassOf, subclass_of):
                self.subclass_of_map[subclass_of].append(class_uri)

    def next_step(self):
        if self.current_step == 0:
            try:
                file_dialog = QFileDialog(self)
                file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png *.bmp)")
                if file_dialog.exec_():
                    file_path = file_dialog.selectedFiles()[0]
                    pixmap = QPixmap(file_path)
                    self.image_label.setPixmap(pixmap)
                    self.image_label.show()
                    self.current_step = 1
                    self.next_button.show()
                    self.upload_button.hide()
            except Exception as e:
                print("Error uploading image:", e)

        elif self.current_step == 1:
            self.next_button.hide()
            self.upload_button.hide()
            self.scene_description_input.show()
            self.process_button.show()
            self.current_step = 2

    def upload_image(self):
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png *.bmp)")
            if file_dialog.exec_():
                self.file_path = file_dialog.selectedFiles()[0]
                pixmap = QPixmap(self.file_path)
                self.image_label.setPixmap(pixmap)
                self.image_label.show()
                self.current_step = 1
                self.next_button.show()
        except Exception as e:
            print("Error uploading image:", e)


    def list_entities_and_relations(self):
        classes = set(self.g.subjects(RDF.type, OWL.Class))
        entities = [str(c).replace(str(self.MY_NS), "") for c in classes if str(c).startswith(str(self.MY_NS))]
        entities += [str(c).replace(str(self.TIME_NS), "") for c in classes if str(c).startswith(str(self.TIME_NS))]
        entities += [str(c).replace(str(self.GEOSPATIAL_NS), "") for c in classes if str(c).startswith(str(self.GEOSPATIAL_NS))]

        relations = set(self.g.subjects(RDF.type, OWL.ObjectProperty))
        relations_list = [str(r).replace(str(self.MY_NS), "") for r in relations if str(r).startswith(str(self.MY_NS))]
        relations_list += [str(r).replace(str(self.TIME_NS), "") for r in relations if str(r).startswith(str(self.TIME_NS))]
        relations_list += [str(r).replace(str(self.GEOSPATIAL_NS), "") for r in relations if str(r).startswith(str(self.GEOSPATIAL_NS))]

        return entities, relations_list

    def process_scene_description(self):
        scene_description = self.scene_description_input.toPlainText()

        if scene_description:
            new_classes, new_relations = self.analyze_scene_description(scene_description)

            message = ""
            if new_classes or new_relations:
                message += "New items to be added:\n"
                if new_classes:
                    message += "Classes: " + ", ".join(new_classes) + "\n"
                if new_relations:
                    message += "Relations: " + ", ".join(new_relations) + "\n"

            message += "\nProceeding to create/update the scene graph."
            QMessageBox.information(self, "Information", message)

            # Proceed with scene graph creation/update
            self.generate_instance_from_scene_description(scene_description)
            self.serialize_graph()  # Optionally save the updated graph

        else:
            QMessageBox.warning(self, "Warning", "No scene description provided.")

    def get_or_create_instance(self, instance_name, class_name=None):
        instance_uri = self.existing_instances.get(instance_name)

        if instance_uri:
            return instance_uri

        random_number = random.randint(1, 1000)
        instance_identifier = f"{instance_name}{random_number}"
        instance_uri = URIRef(self.MY_NS + instance_identifier)
        self.existing_instances[instance_name] = instance_uri

        if class_name:
            self.g.add((instance_uri, RDF.type, OWL.NamedIndividual))
            self.g.add((instance_uri, RDF.type, self.MY_NS[class_name]))

        return instance_uri

    def analyze_scene_description(self, scene_description):
        new_classes = set()
        new_relations = set()

        statements = scene_description.split("\n")
        for statement in statements:
            parts = statement.strip().split(" ")
            if len(parts) == 3:
                subject_instance_identifier, property_name, object_instance_identifier = parts

                subject_class_name = re.sub(r'\d+', '', subject_instance_identifier)
                object_class_name = re.sub(r'\d+', '', object_instance_identifier)

                # Check if class exists, if not, add to new_classes
                if not self.class_exists(subject_class_name):
                    new_classes.add(subject_class_name)
                if not self.class_exists(object_class_name):
                    new_classes.add(object_class_name)

                # Check if relation exists, if not, add to new_relations
                if not self.relation_exists(property_name):
                    new_relations.add(property_name)

                # Check if instances already exist for subject and object names
                subject_name = subject_instance_identifier.replace(subject_class_name, '')
                object_name = object_instance_identifier.replace(object_class_name, '')

                subject_uri = self.get_or_create_instance(subject_name)

                object_uri = self.get_or_create_instance(object_name)

        return new_classes, new_relations

    def class_exists(self, class_name):
        class_uri = URIRef(self.MY_NS + class_name)
        if (class_uri, RDF.type, OWL.Class) in self.g:
            subclass_of_values = [o for s, p, o in self.g.triples((class_uri, RDFS.subClassOf, None))]
            return True, subclass_of_values
        else:
            return False, []

    def add_new_class(self, class_name):
        class_uri = URIRef(self.MY_NS + class_name)
        if not self.class_exists(class_name):
            self.g.add((class_uri, RDF.type, OWL.Class))
            print(f"Added new class: {class_name}")
        return class_uri

    def relation_exists(self, relation_name):
        relation_uri = URIRef(self.MY_NS + relation_name)
        return (relation_uri, RDF.type, OWL.ObjectProperty) in self.g

    def add_new_relation(self, relation_name):
        relation_uri = URIRef(self.MY_NS + relation_name)
        if not self.relation_exists(relation_name):
            self.g.add((relation_uri, RDF.type, OWL.ObjectProperty))
            print(f"Added new relation: {relation_name}")
        return relation_uri

    def create_sensor_instance(self, instance_name, class_name=None, created_instances=None):
        if created_instances is None:
            created_instances = set()

        random_number = random.randint(1, 1000)
        instance_identifier = f"{instance_name}{random_number}"
        instance_uri = URIRef(self.MY_NS + instance_identifier)

        if class_name:
            self.g.add((instance_uri, RDF.type, OWL.NamedIndividual))
            self.g.add((instance_uri, RDF.type, self.MY_NS[class_name]))

            # Create instances for observable properties
            if class_name == "BicycleSensor":
                observes_uri = self.MY_NS["observes"]
                observable_properties = ["Latitude", "Longitude", "BicycleBrakesCondition", "Speed", "ProximityToClosestVehicle", "ProximityToClosestPedestrian"]
                location_property_instance_uri = None
                for property_name in observable_properties:
                    property_instance_name = f"{property_name}{random_number}"
                    bic_property_instance_uri = URIRef(self.MY_NS + property_instance_name)
                    # Assuming property_name is a class in your ontology
                    self.g.add((bic_property_instance_uri, RDF.type, self.MY_NS[property_name]))
                    self.g.add((instance_uri, observes_uri, bic_property_instance_uri))
                    observed_by_uri = self.MY_NS["observedBy"]
                    self.g.add((bic_property_instance_uri, observed_by_uri, instance_uri))
                    if property_name == "Location":
                        location_property_instance_uri = bic_property_instance_uri
                    # Keep track of the created instances
                    created_instances.add(bic_property_instance_uri)

            if class_name == "VehicleSensor":
                observes_uri = self.MY_NS["observes"]
                observable_properties = ["Latitude", "Longitude", "DoorLockStatus", "Acceleration", "Speed", "ProximityToClosestVehicle", "ProximityToClosestPedestrian"]
                location_property_instance_uri = None
                for property_name in observable_properties:
                    property_instance_name = f"{property_name}{random_number}"
                    veh_property_instance_uri = URIRef(self.MY_NS + property_instance_name)
                    # Assuming property_name is a class in your ontology
                    self.g.add((veh_property_instance_uri, RDF.type, self.MY_NS[property_name]))
                    self.g.add((instance_uri, observes_uri, veh_property_instance_uri))
                    observed_by_uri = self.MY_NS["observedBy"]
                    self.g.add((veh_property_instance_uri, observed_by_uri, instance_uri))
                    if property_name == "Location":
                        location_property_instance_uri = veh_property_instance_uri
                    # Keep track of the created instances
                    created_instances.add(veh_property_instance_uri)

            if class_name == "EnvironmentalSensor":
                observes_uri = self.MY_NS["observes"]
                observable_properties = ["Temperature", "Humidity", "WindSpeed", "AtmosphericPressure"]
                for property_name in observable_properties:
                    property_instance_name = f"{property_name}{random_number}"
                    env_property_instance_uri = URIRef(self.MY_NS + property_instance_name)
                    # Assuming property_name is a class in your ontology
                    self.g.add((env_property_instance_uri, RDF.type, self.MY_NS[property_name]))
                    self.g.add((instance_uri, observes_uri, env_property_instance_uri))
                    observed_by_uri = self.MY_NS["observedBy"]
                    self.g.add((env_property_instance_uri, observed_by_uri, instance_uri))
                    # Keep track of the created instances
                    created_instances.add(env_property_instance_uri)

            if class_name == "SmartPhoneSensor":
                observes_uri = self.MY_NS["observes"]
                observable_properties = ["RespiratoryRate", "HeartRate"]
                for property_name in observable_properties:
                    property_instance_name = f"{property_name}{random_number}"
                    smart_phone_property_instance_uri = URIRef(self.MY_NS + property_instance_name)
                    # Assuming property_name is a class in your ontology
                    self.g.add((smart_phone_property_instance_uri, RDF.type, self.MY_NS[property_name]))
                    self.g.add((instance_uri, observes_uri, smart_phone_property_instance_uri))
                    observed_by_uri = self.MY_NS["observedBy"]
                    self.g.add((smart_phone_property_instance_uri, observed_by_uri, instance_uri))
                    # Keep track of the created instances
                    created_instances.add(smart_phone_property_instance_uri)

        return instance_uri

    def create_instance_with_sensor(self, subject_instance_uri, subject_class_name):
        subclass_of_values = self.class_exists(subject_class_name)[1]
        if any(subclass_uri == self.MY_NS["TwoWheeledVehicle"] for subclass_uri in subclass_of_values):
            # Check if a bicycle sensor instance for this subject instance has already been created
            if subject_instance_uri not in self.bicycle_sensor_instances_created:
                bicycle_sensor_instance_uri = self.create_sensor_instance("BicSensor", "BicycleSensor", set())
                is_installed_on_uri = self.MY_NS["isInstalledOn"]
                has_sensor_uri = self.MY_NS["hasSensor"]
                self.g.add((bicycle_sensor_instance_uri, is_installed_on_uri, subject_instance_uri))
                self.g.add((subject_instance_uri, has_sensor_uri, bicycle_sensor_instance_uri))
                # Keep track of the created bicycle sensor instances
                self.bicycle_sensor_instances_created.add(subject_instance_uri)
                env_sensor_instance_uri = self.create_sensor_instance("EnvSensor", "EnvironmentalSensor", set())

        if subject_class_name == "Rider":
            phone_sensor_instance_uri = self.create_sensor_instance("SmartPhoneSensor", "SmartPhoneSensor", set())
            has_sensor_uri = self.MY_NS["hasSensor"]
            self.g.add((subject_instance_uri, has_sensor_uri, phone_sensor_instance_uri))

        if any(subclass_uri == self.MY_NS["FourWheeledVehicle"] for subclass_uri in subclass_of_values):
            # Check if a vehicle sensor instance for this subject instance has already been created
            if subject_instance_uri not in self.vehicle_sensor_instances_created:
                vehicle_sensor_instance_uri = self.create_sensor_instance("VehSensor", "VehicleSensor", set())
                is_installed_on_uri = self.MY_NS["isInstalledOn"]
                has_sensor_uri = self.MY_NS["hasSensor"]
                self.g.add((vehicle_sensor_instance_uri, is_installed_on_uri, subject_instance_uri))
                self.g.add((subject_instance_uri, has_sensor_uri, vehicle_sensor_instance_uri))
                # Keep track of the created bicycle sensor instances
                self.vehicle_sensor_instances_created.add(subject_instance_uri)
                env_sensor_instance_uri = self.create_sensor_instance("EnvSensor", "EnvironmentalSensor", set())

    def generate_instance_from_scene_description(self, scene_description):
        # Split the scene description into triples
        triples = [line.strip().split() for line in scene_description.split("\n")]

        # Group triples by subject and object
        triples_by_subject = {}
        triples_by_object = {}
        for triple in triples:
            subject, predicate, obj = triple
            if subject not in triples_by_subject:
                triples_by_subject[subject] = []
            if obj not in triples_by_object:
                triples_by_object[obj] = []
            triples_by_subject[subject].append((subject, predicate, obj))
            triples_by_object[obj].append((subject, predicate, obj))

        # Create an instance of "Scene" with a random ID
        scene_instance_name = f"Scene_{uuid.uuid4().hex}"
        scene_instance_uri = self.get_or_create_instance(scene_instance_name, "Scene")

        # Create instances for subjects and objects
        for subject in triples_by_subject:
            subject_class_name = re.sub(r'\d+', '', subject)
            if not self.class_exists(subject_class_name):
                self.add_new_class(subject_class_name)
                print(f"Created new class: {subject_class_name}")
            subject_instance_uri = self.get_or_create_instance(subject, subject_class_name)
            self.create_instance_with_sensor(subject_instance_uri, subject_class_name)
            subclass_of_values = self.class_exists(subject_class_name)[1]
            if any(subclass_uri == self.MY_NS["TwoWheeledVehicle"] or subclass_uri == self.MY_NS["FourWheeledVehicle"] or subclass_uri == self.MY_NS["Person"] for subclass_uri in subclass_of_values):
                # Relate subject to the scene
                self.g.add((subject_instance_uri, self.MY_NS["isAParticipantOfScene"], scene_instance_uri))
                self.g.add((scene_instance_uri, self.MY_NS["includes"], subject_instance_uri))
                print(f"Created Scene Relation for Subject")

        for obj in triples_by_object:
            obj_class_name = re.sub(r'\d+', '', obj)
            if not self.class_exists(obj_class_name):
                self.add_new_class(obj_class_name)
                print(f"Created new class: {obj_class_name}")
            obj_instance_uri = self.get_or_create_instance(obj, obj_class_name)
            if any(subclass_uri == self.MY_NS["TwoWheeledVehicle"] or subclass_uri == self.MY_NS["FourWheeledVehicle"] or subclass_uri == self.MY_NS["Person"] for subclass_uri in subclass_of_values):
                # Relate subject to the scene
                self.g.add((obj_instance_uri, self.MY_NS["isAParticipantOfScene"], scene_instance_uri))
                self.g.add((scene_instance_uri, self.MY_NS["includes"], obj_instance_uri))
                print(f"Created Scene Relation for Subject")

        # Add relations based on grouped triples
        for triple in triples:
            subject, predicate, obj = triple
            subject_instance_uri = self.existing_instances[subject]
            obj_instance_uri = self.existing_instances[obj]
            if not self.relation_exists(predicate):
                self.add_new_relation(predicate)
                print(f"Created new relation: {predicate}")
            property_uri = self.add_new_relation(predicate)
            self.g.add((subject_instance_uri, property_uri, obj_instance_uri))
            print(f"Created relation: {subject} {predicate} {obj}")


    def serialize_graph(self):
        # Serialize and save the graph
        self.g.serialize(destination="C:/Users/ardesilva/Downloads/updated_ravdKGMerge999.owl", format="xml")

def main():
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
     main()
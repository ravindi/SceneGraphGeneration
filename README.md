Overview
The Scene Graph Generation Application is a Python-based GUI tool that allows users to upload images, input scene descriptions, and generate scene graphs based on a pre-defined ontology. The application processes the input to identify entities, relationships, and contexts, creating a structured RDF-based representation of the scene, including the addition of sensors and observable properties for smart entities.

Features
Image Upload and Display:

Upload images in common formats (.jpg, .jpeg, .png, .bmp).
Display the uploaded image in the application.
Scene Description Input:

Input scene descriptions in natural language or structured triples.
Automatically analyze the input to identify new classes, relations, and instances.
Ontology Integration:

Utilize an ontology (ravdKGMerged1.owl) for structured knowledge representation.
Dynamically extend the ontology by adding new classes, relations, and instances as needed.
Sensor Integration:

Automatically generate sensor instances for entities such as bicycles, vehicles, riders, and environmental conditions.
Link sensor instances to their parent entities with appropriate relationships.
Scene Graph Generation:

Generate scene graphs with participants, relationships, and contextual information.
Group participants and objects under a unique scene instance.
Graph Serialization:

Serialize the updated RDF graph into an OWL file for further use in ontology management tools like Protégé.
Requirements
Software Requirements
Python 3.7 or higher
PyQt5 for GUI
rdflib for RDF graph manipulation
Pillow for image processing
opencv-python for additional image handling
spacy for natural language processing
ultralytics for object detection (if extended functionality is used)
Ontology File
Ensure the ontology file ravdKGMerged1.owl is located in the application's working directory.

Installation
Install the required Python packages:
bash
Copy
Edit
pip install PyQt5 rdflib Pillow opencv-python spacy ultralytics
Download or clone the application source code.
Place the ontology file ravdKGMerged1.owl in the same directory as the application.
Usage
Starting the Application
Run the application using the following command:

bash
Copy
Edit
python main.py
Steps to Generate a Scene Graph
Upload Image:
Click on the "Upload Image" button to select and display an image.
Input Scene Description:
Enter a scene description in the text editor (e.g., Bicycle123 isNear Car456).
Click "Process Scene Description" to analyze and update the ontology.
Scene Graph Generation:
The application creates or updates instances, relationships, and sensors based on the scene description.
Save Updated Ontology:
The updated RDF graph is serialized and saved to updated_ravdKGMerge999.owl.

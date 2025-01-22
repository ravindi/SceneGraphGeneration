# Scene Graph Generation Application

## 🌟 Overview
The **Scene Graph Generation Application** is a Python-based GUI tool for:
- Uploading images
- Inputting scene descriptions
- Generating scene graphs based on a pre-defined ontology

The application processes inputs to identify **entities**, **relationships**, and **contexts**, creating an RDF-based structured representation.

---

## ✨ Features
- **Image Upload & Display**  
  Upload and display images in common formats (`.jpg`, `.jpeg`, `.png`, `.bmp`).
  
- **Scene Description Input**  
  Input natural language or structured triples to describe a scene.

- **Ontology Integration**  
  Utilize and extend an ontology (`ravdKGMerged1.owl`) dynamically.

- **Sensor Integration**  
  Automatically add sensors (e.g., Bicycle, Vehicle, Environmental) to smart entities.

- **Scene Graph Generation**  
  Generate RDF-based graphs including participants, relationships, and contexts.

- **Graph Serialization**  
  Save the updated RDF graph in OWL format for further use.

---

## 📋 Requirements

### Software Requirements
- **Python 3.7 or higher**
- Libraries:
  - `PyQt5`
  - `rdflib`
  - `Pillow`
  - `opencv-python`
  - `spacy`
  - `ultralytics`

### Ontology File
- Place the ontology file `ravdKGMerged1.owl` in the working directory.

### Installation
```bash
pip install PyQt5 rdflib Pillow opencv-python spacy ultralytics

## 🚀 Usage

### Starting the Application
Run the following command:
```bash
python main.py

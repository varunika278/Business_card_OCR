from flask import Flask, request, render_template, send_from_directory
import os
import easyocr
import cv2
import re
import Levenshtein
import matplotlib.pyplot as plt

app = Flask(__name__)

# Create the 'uploads' and 'results' directories if they don't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('results', exist_ok=True)

# Initialize the reader
reader = easyocr.Reader(['en'])

# Keywords for identifying address-like text
keywords = [
    'road', 'floor', ' st ', 'st,', 'street', ' dt ', 'district',
    'near', 'beside', 'opposite', ' at ', ' in ', 'center', 'main road',
    'state', 'country', 'post', 'zip', 'city', 'zone', 'mandal', 'town', 'rural',
    'circle', 'next to', 'across from', 'area', 'building', 'towers', 'village',
    ' ST ', ' VA ', ' VA,', ' EAST ', ' WEST ', ' NORTH ', ' SOUTH '
]

# State names to check similarity
states = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 
    'Haryana','Hyderabad', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
    'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'United States', 'China', 'Japan', 'Germany', 'United Kingdom', 'France', 'India', 
    'Canada', 'Italy', 'South Korea', 'Russia', 'Australia', 'Brazil', 'Spain', 'Mexico', 'USA', 'UK'
]

# Email regex pattern
email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Designations to ignore
designations = [
    'sales', 'teacher', 'helper', 'educator', 'manager', 'director', 'consultant',
    'executive', 'officer', 'assistant', 'supervisor', 'administrator',
    'coordinator', 'advisor', 'representative', 'clerk', 'technician', 'engineer','counsellor ','cheif'
    'analyst', 'designer', 'developer', 'programmer', 'planner', 'strategist', 'senior', 'junior', 'intern','internship', 'apprentice','appiienitie'
]

companySuffix = ['pvt','private','limited','ltd','public','service','technologies','technology','solutions','services']

# Address pattern for continuous digits
digit_pattern = r'\d{6,7}'

# Function to calculate string similarity
def string_similarity(s1, s2):
    distance = Levenshtein.distance(s1, s2)
    similarity = 1 - (distance / max(len(s1), len(s2)))
    return similarity * 100

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file:
        filename = file.filename
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        # Perform OCR and process the image
        image = cv2.imread(filepath)
        results = reader.readtext(image)

        # Extract results for processing
        result_text = [result[1] for result in results]

        PH = []
        PHID = []
        areas = []
        bbox_dict = {}

        # Extract phone numbers and their indices
        for i, (bbox, text, prob) in enumerate(results):
            match = re.search(r'(?:ph|phone|phno)?\s*(?:[+-]?\d\s*[\(\)]*){7,}', text)
            if match and len(re.findall(r'\d', text)) > 7:
                PH.append(text)
                PHID.append(i)

            # Calculate the bounding box area
            (top_left, top_right, bottom_right, bottom_left) = bbox
            width = abs(top_right[0] - top_left[0])
            height = abs(bottom_left[1] - top_left[1])
            area = width * height
            areas.append((width, height, top_left[1], i))  # Append width, height, vertical position (y coordinate), and index
            bbox_dict[i] = (bbox, text)

        # Sort areas based on area size (descending) and vertical position (ascending)
        sorted_areas = sorted(areas, key=lambda x: (-(x[0] * x[1]), x[2]))

        # Find and exclude address-like text, emails, and designations
        ADD = set()
        AID = []
        for i, text in enumerate(result_text):
            if (
                any(keyword in text.lower() for keyword in keywords) or
                re.search(digit_pattern, text) or
                re.search(email_pattern, text.lower()) or
                any(designation in text.lower() for designation in designations)
            ):
                ADD.add(text)
                AID.append(i)
            else:
                for state in states:
                    if string_similarity(state.lower(), text.lower()) > 50:
                        ADD.add(text)
                        AID.append(i)
                        break

        # Assuming the largest area text as the organization name based on width or height
        if sorted_areas:
            organization_index = sorted_areas[0][3]
            organization_name = results[organization_index][1]
            
            # Find the bounding box above the designation bounding box
            person_name = "Not found"
            designation_bbox_y = None
            
            for width, height, y, idx in sorted_areas:
                if idx in AID and any(designation in results[idx][1].lower() for designation in designations):
                    designation_bbox_y = y
                    break
            
            if designation_bbox_y is not None:
                potential_names = []
                for width, height, y, idx in sorted_areas:
                    if y < designation_bbox_y and not re.search(email_pattern, results[idx][1].lower()) and idx not in AID:
                        potential_names.append((y, results[idx][1]))
                
                # Select the one closest to the designation
                if potential_names:
                    person_name = min(potential_names, key=lambda x: designation_bbox_y - x[0])[1]
        else:
            organization_name = "Not found"
            person_name = "Not found"

        # Prepare the phone number output
        ph_str = ', '.join(PH) if PH else "Not found"

        # Annotate the image with bounding boxes and text
        for (bbox, text, prob) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            # Draw the bounding box and text
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Save the annotated image
        annotated_image_path = os.path.join('results', filename)
        cv2.imwrite(annotated_image_path, image)

        return render_template('results.html', person_name=person_name, organization_name=organization_name, phone_number=ph_str, image_path=annotated_image_path)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/results/<filename>')
def send_annotated_file(filename):
    return send_from_directory('results', filename)

if __name__ == '__main__':
    app.run(debug=True)

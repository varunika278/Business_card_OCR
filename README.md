# Business Card OCR  

The **Business Card OCR System** is an advanced Optical Character Recognition (OCR) tool designed to extract key information from business card images. This system uses EasyOCR and NLP techniques to identify and process details like names, designations, organizations, contact numbers, and addresses.  

## Key Features  
- **Text Extraction**: Extracts textual data using EasyOCR.  
- **Information Parsing**: Identifies key details such as:  
  - **Person Name**: Recognizes the individual's name.  
  - **Organization Name**: Detects the company or organization.  
  - **Phone Numbers**: Extracts valid contact numbers.  
  - **Addresses**: Identifies address-like details from text.  
- **Annotated Output**: Generates an annotated image with bounding boxes and extracted text.  

## Technologies  
- **Python**: Core programming language.  
- **Flask**: For developing the web application.  
- **EasyOCR**: To perform text extraction from images.  
- **OpenCV**: For image processing and annotation.  
- **Levenshtein**: To calculate text similarity for state names and other entities.  
- **HTML/CSS & JavaScript**: For creating the interactive web interface.  

## Installation  
1. Clone the repository:  
   ```bash  
   https://github.com/varunika278/Business_card_OCR.git
   ```  
2. Navigate to the project directory:  
   ```bash  
   cd business-card-ocr  
   ```  
3. Install the required dependencies:  
   ```bash  
   pip install -r requirements.txt  
   ```  
4. Run the application:  
   ```bash  
   python app.py  
   ```  

## Usage  
1. Upload a business card image.  
2. View the extracted information and download the annotated image.  

## Directory Structure  
- **uploads/**: Stores uploaded images.  
- **results/**: Stores annotated images.  
- **templates/**: Contains HTML files for the web interface.  

## Acknowledgements  
- **EasyOCR**: For OCR functionality.  
- **OpenCV**: For image processing.  
- **Levenshtein**: For text similarity computation.  

# Remove-Brand-Logo 🚀  
_Automatically remove brand logos and unwanted slides from PDFs_  

## Overview  

**Remove-Brand-Logo** is a Python script that detects and removes brand logos from slides in PDF documents. It also allows the automatic deletion of specific slides based on an offset list. Ideal for cleaning up virtual lecture slides, presentations, and study materials.  

### Features  
✅ Remove brand logos from PDF slides using coordinate-based cropping  
✅ Automatically delete slides based on position (offset list)  
✅ Fast and efficient processing using PyMuPDF and Pillow  
✅ Simple command-line interface  

## Installation  

Ensure you have Python installed, then install the required dependencies:  

```bash
pip install pillow PyMuPDF
```

## Usage  

Run the script with the following command:  

```bash
python remove_brand_logo.py input.pdf output_folder --offset_list "15" --rect_coords 0 750 100 800
```

### Parameters  
- **`input.pdf`**: Path to the PDF file to process  
- **`output_folder`**: Directory where the cleaned PDF will be saved  
- **`--offset_list "15"`**: Remove slide 15 (comma-separated values for multiple slides)  
- **`--rect_coords 0 750 100 800`**: Define the rectangular area (x1, y1, x2, y2) for logo removal  

## Example Use Case  
Need to clean up university slides? This script helps by removing distracting logos and unwanted pages, improving readability and focus.  

## Why Use This Script?  
- Save time manually editing PDFs  
- Improve document clarity by removing unnecessary branding  
- Lightweight, fast, and does not require expensive PDF editing software  

## Disclaimer  
This script is for **personal and educational use only**. Please respect copyright laws when modifying documents.  

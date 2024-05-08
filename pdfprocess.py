import fitz
import pytesseract
from PIL import Image
import PyPDF2
import re
import os
import shutil
import tkinter as tk
from tkinter import filedialog
import logging

# Configure logging
log_filename = "pdf_processor_log.txt"
logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Set the path to the Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"


def extract_image_from_pdf(pdf_path):
    images = []
    pdf_document = fitz.open(pdf_path)

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        images.append(image)

    pdf_document.close()
    return images

def perform_ocr(images):
    extracted_text = []

    for image in images:
        text = pytesseract.image_to_string(image, lang='eng')
        # print(text)
        extracted_text.append(text)
        # print(extracted_text)

    return extracted_text

def process_extracted_text(extracted_text):
    user_info_dict = {'Primary Taxpayer': {}, 'Secondary Taxpayer': {}}
    current_taxpayer = None
    tax_year = None

    for line in extracted_text[0].split('\n'):
        # Identify if this is Primary or Secondary Taxpayer
        if 'Primary Taxpayer' in line:
            current_taxpayer = 'Primary Taxpayer'
        elif 'Secondary Taxpayer' in line:
            current_taxpayer = 'Secondary Taxpayer'

        # Extract tax year information        
        if 'Tax Year' in line:
            _, tax_year = map(str.strip, line.split('Tax Year', 1))
            # Clean up tax_year, removing any invalid characters
            tax_year = tax_year.replace(':', '').strip()
        elif 'Tox Year' in line:
            _, tax_year = map(str.strip, line.split('Tox Year', 1))
            # Clean up tax_year, removing any invalid characters
            tax_year = tax_year.replace(':', '').strip()  

        # # tax_year defaults to 2022 or 2023 (can be modified)
        else:
            tax_year = '2023'   

        # Check for keywords related to taxpayer information
        for keyword in ['First Name', 'Last Name', 'Last Four', 'TaxReturn ID']:
            if keyword in line:
                _, current_value = map(str.strip, line.split(keyword, 1))

                # Add the key-value pair to the appropriate taxpayer dictionary
                user_info_dict[current_taxpayer][keyword] = current_value

    # Add 'Tax Year' to the user_info_dict
    user_info_dict['Tax Year'] = tax_year

    # print(user_info_dict)

    return user_info_dict

# main function to determine whether to use OCR or non-OCR approach
def process_pdf(pdf_path, destination_folder):
    # open the pdf 
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # extract the text
        text = pdf_reader.pages[0].extract_text()

    # Check if PDF has text content
    if text.strip():
        # use OCR approach
        extract_data_and_create_with_OCR(pdf_path, destination_folder)
    else:
        # use non-OCR approach
        extract_data_and_create(pdf_path, destination_folder)


# conventional method of converting pdf to image, then extract the data
def extract_data_and_create(pdf_path, destination_folder):

    # Create an image using the pdf
    pdf_image = extract_image_from_pdf(pdf_path)

    # Perform OCR to extract the text from the image
    ocr_text = perform_ocr(pdf_image)

    # Add all the information to the dictionary 
    user_info_dict = process_extracted_text(ocr_text)  # this is all the information needed for the functionality

    # Check if values exist in the user_info_dict
    if user_info_dict.get('Tax Year') and (user_info_dict.get('Primary Taxpayer') or user_info_dict.get('Secondary Taxpayer')):
        tax_year = user_info_dict['Tax Year']
        primary_first_name = user_info_dict['Primary Taxpayer'].get('First Name', '').strip().upper()
        primary_last_name = user_info_dict['Primary Taxpayer'].get('Last Name', '').strip().upper()
        secondary_first_name = user_info_dict['Secondary Taxpayer'].get('First Name', '').strip().upper()
        secondary_first_name = secondary_first_name.replace(',', '')

        # Replace invalid characters in names with underscores
        primary_first_name = primary_first_name.replace(':', '_')
        primary_last_name = primary_last_name.replace(':', '_')
        secondary_first_name = secondary_first_name.replace(':', '_')
        secondary_first_name = secondary_first_name.replace('+', '_')

        # Generate base folder name
        if secondary_first_name:
            base_folder_name = f"{tax_year}_{primary_last_name}_{primary_first_name}+{secondary_first_name}"
        else:
            base_folder_name = f"{tax_year}_{primary_last_name}_{primary_first_name}"

        # Check if the base folder already exists
        folder_path = os.path.join(destination_folder, base_folder_name)

        if os.path.exists(folder_path):
            subscript = 1
            while True:
                if secondary_first_name:
                    new_file_name = f"{tax_year}_{primary_last_name}_{primary_first_name}+{secondary_first_name} ({subscript}).pdf"
                else:
                    new_file_name = f"{tax_year}_{primary_last_name}_{primary_first_name}({subscript}).pdf"
                new_file_path = os.path.join(folder_path, new_file_name)
                if not os.path.exists(new_file_path):
                    break
                subscript += 1
            
            # Duplicate file
            shutil.copy(pdf_path, new_file_path)

            # Delete the original file
            os.remove(pdf_path)

            # print(f"New PDF created and saved as: {new_file_path}")
            logging.info(f"New PDF created and saved as: {new_file_path}")

        else:
            # If the base folder doesn't exist, create the base folder and add the file
            os.makedirs(folder_path)

            # Generate new file name
            if secondary_first_name:
                new_file_name = f"{tax_year}_{primary_last_name}_{primary_first_name}+{secondary_first_name}.pdf"
            else:
                new_file_name = f"{tax_year}_{primary_last_name}_{primary_first_name}.pdf"

            new_file_path = os.path.join(folder_path, new_file_name)

            # Duplicate file
            shutil.copy(pdf_path, new_file_path)

            # Delete the original file
            os.remove(pdf_path)

            # print(f"New PDF created and saved as: {new_file_path}")
            logging.info(f"New PDF created and saved as: {new_file_path}")

    # Handle invalid case
    else:
        # print(user_info_dict)
        # print("Required information not found in the PDF.")
        logging.warning("Required information not found in the PDF.")



# extract_data_and_create with OCR
def extract_data_and_create_with_OCR(pdf_path, destination_folder):
    # Extract text from the given PDF file
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = pdf_reader.pages[0].extract_text()
    
    tax_year_match = re.search(r'Tax Year:\s*(\d{4})', text)
    primary_first_name_match = re.search(r'Primary Taxpayer\s*First Name\s+(.+)', text)
    primary_last_name_match = re.search(r'Last Name\s+(.+)', text)

    secondary_first_name_match = re.search(r'Secondary Taxpayer\s*First Name\s+(.+)', text)
    # print(secondary_first_name_match)
    # secondary_last_name_match = re.search(r'Secondary Taxpayer\s*Last Name\s+(.+)', text)

    tax_number = re.search(r'Last Four\s+(.+)', text)

    # Check if values match
    if tax_year_match or primary_first_name_match or primary_last_name_match or secondary_first_name_match:
        tax_year = tax_year_match.group(1)
        primary_first_name = primary_first_name_match.group(1).strip().upper()
        primary_last_name = primary_last_name_match.group(1).strip().upper()
        tax_number = tax_number.group(1).strip()
        if secondary_first_name_match:
            secondary_first_name = secondary_first_name_match.group(1).strip().upper()
        else:
            secondary_first_name = None

        # Generate base folder name
        if secondary_first_name:
            base_folder_name = f"{tax_year}_{primary_last_name}_{primary_first_name}+{secondary_first_name}"
        else:
            base_folder_name = f"{tax_year}_{primary_last_name}_{primary_first_name}"

        # Check if the base folder already exists
        folder_path = os.path.join(destination_folder, base_folder_name)

        if os.path.exists(folder_path):
            # If the base folder exists, add subscript to the file
            subscript = 1
            while True:
                new_file_name = f"{base_folder_name} ({subscript}).pdf"
                new_file_path = os.path.join(folder_path, new_file_name)
                if not os.path.exists(new_file_path):
                    break
                subscript += 1

            # Duplicate file
            shutil.copy(pdf_path, new_file_path)

            # Delete the original file
            os.remove(pdf_path)

            # print(f"New PDF created and saved as: {new_file_path}")
            logging.info(f"New PDF created and saved as: {new_file_path}")

        else:
            # If the base folder doesn't exist, create the base folder and add the file
            os.makedirs(folder_path, exist_ok=True)

            # Generate new file name
            if secondary_first_name:
                new_file_name = f"{tax_year}_{primary_last_name}_{primary_first_name}+{secondary_first_name}.pdf"
            else:
                new_file_name = f"{tax_year}_{primary_last_name}_{primary_first_name}.pdf"

            new_file_path = os.path.join(folder_path, new_file_name)

            # Duplicate file
            shutil.copy(pdf_path, new_file_path)

            # Delete the original file
            os.remove(pdf_path)

            # print(f"New PDF created and saved as: {new_file_path}")
            logging.info(f"New PDF created and saved as: {new_file_path}")

    # Handle invalid case
    else:
        # print("Required information not found in the PDF.")
        logging.warning("Required information not found in the PDF.")

# Make a class for the PDF processing
class PDFProcessor:
    # constructor
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Processor App")

        self.source_folder_var = tk.StringVar()

        self.create_widgets()
        
    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="PDF Processor App", font=("Helvetica", 16, "bold"), pady=10)
        title_label.pack()

        # Frame for input widgets
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack()

        tk.Label(input_frame, text="Enter the path to the Source folder:").grid(row=0, column=0, sticky="w")
        entry = tk.Entry(input_frame, textvariable=self.source_folder_var, width=30)
        entry.grid(row=0, column=1, padx=10)
        tk.Button(input_frame, text="Browse", command=self.browse_folder).grid(row=0, column=2)

        # Frame for action buttons
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack()

        tk.Button(button_frame, text="Process Files", command=self.process_files).pack()

        # Status labels
        self.success_label = tk.Label(self.root, text="", font=("Helvetica", 11), fg="green")
        self.success_label.pack()

        self.error_label = tk.Label(self.root, text="", font=("Helvetica", 11), fg="red")
        self.error_label.pack()


    # browse for source folder
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.source_folder_var.set(folder_path)

    # function to process the files inside the folder
    def process_files(self):
        source_folder = self.source_folder_var.get()

        if not os.path.exists(source_folder):
            self.error_label.config(text="Error: Source folder does not exist.")
            self.success_label.config(text="")
            return
    
        success_message = "Successfully processed all PDF files in the folder."
        error_message = "Error: Some files could not be processed."

        all_files_processed = True

        for filename in os.listdir(source_folder):
            if filename.lower().endswith(".pdf"):
                source_path = os.path.join(source_folder, filename)
                # main functionality goes here
                try:
                    # extract_data_and_create(source_path, source_folder)
                    process_pdf(source_path, source_folder)
                except Exception as e:
                    # print(f"Error processing {filename}: {str(e)}")
                    logging.info(f"Error processing {filename}: {str(e)}")
                    all_files_processed = False
        
         # Update labels based on the processing result
        if all_files_processed:
            self.success_label.config(text=success_message)
            self.root.after(5000, lambda: self.success_label.config(text=""))  # Hide success message after 5 seconds
            # self.error_label.config(text="")
        else:
            # self.success_label.config(text="")
            self.error_label.config(text=error_message)
            self.root.after(5000, lambda: self.error_label.config(text=""))  # Hide error message after 5 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFProcessor(root)
    root.mainloop()
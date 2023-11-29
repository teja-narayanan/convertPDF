# PDF Processor Readme

## Overview:
The "PDF Processor" is a Python program designed to extract specific information from PDF files related to tax documents. The extracted data includes the tax year, primary taxpayer's first and last name, and the last four digits of the tax identification number. The program organizes and stores the processed PDFs in a new folder structure based on the extracted information.

### Features:
-> PDF Data Extraction:

Utilizes the PyPDF2 library to extract text data from the first page of PDF files.
Employs regular expressions to identify and extract relevant information such as tax year, primary taxpayer's first and last name, and the last four digits of the tax identification number.
Folder and File Organization:

Creates a new folder structure based on the extracted information.
Each folder is named using a format: TaxYear_LastName_FirstName.
Generates a new PDF file within the corresponding folder, following the format: TaxYear_LastName_FirstName.pdf.

-> File Handling:
Duplicates the original PDF file to the newly created folder.
Deletes the original PDF file from the source folder.
User Interface with Streamlit:

Provides a simple user interface using the Streamlit library.
Takes the path to the source folder as user input.
Allows the user to initiate the processing of PDF files with a button click.

-> Usage:
  Source Folder Input:
  Enter the path to the source folder containing the PDF files when prompted.
  
  Processing:
  Click the "Process Files" button to initiate the PDF processing.
  
  Feedback:
  
  Receive feedback on the processing status, including success messages and potential errors.
  View the console output for detailed information on each processed file.
  
  Requirements:
  Python 3.x
  PyPDF2
  Streamlit
  
  How to Run:
  Install the required dependencies by running:

  ```bash
  Copy code
  pip install PyPDF2 streamlit
  ```
  
Run the program:

``` bash
Copy code
python your_script_name.py
```
Replace your_script_name.py with the actual name of your Python script.

Follow the instructions in the Streamlit interface to provide the source folder path and initiate the PDF processing.

Notes:
Ensure that the source folder exists before running the program.
The program is designed to process PDF files only.

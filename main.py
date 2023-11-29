import streamlit as st
import PyPDF2
import re
import os
import shutil
from pathlib import Path

# extract_data_and_create
def extract_data_and_create(pdf_path, destination_folder):
    #extract text from given pdf file
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = pdf_reader.pages[0].extract_text()

    tax_year_match = re.search(r'Tax Year:\s*(\d{4})', text)
    primary_first_name_match = re.search(r'Primary Taxpayer\s*First Name\s+(.+)', text)
    primary_last_name_match = re.search(r'Last Name\s+(.+)', text)
    tax_number = re.search(r'Last Four\s+(.+)', text)

    # Check if values match
    if tax_year_match and primary_first_name_match and primary_last_name_match:
        tax_year = tax_year_match.group(1)
        primary_first_name = primary_first_name_match.group(1).strip().upper()
        primary_last_name = primary_last_name_match.group(1).strip().upper()
        tax_number = tax_number.group(1).strip()

        # Generate new folder name
        folder_name = f"{tax_year}_{primary_last_name}_{primary_first_name}"
        folder_path = os.path.join(destination_folder, folder_name)

        # Create a new folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Generate new file name
        new_file_name = f"{tax_year}_{primary_last_name}_{primary_first_name}.pdf"
        new_file_path = os.path.join(folder_path, new_file_name)

        # duplicate file
        shutil.copy(pdf_path, new_file_path)

        # Delete the original file
        os.remove(pdf_path)

        print(f"New PDF created and saved as: {new_file_path}")
        print(f"Original PDF deleted: {pdf_path}")

    # handle invalid case
    else:
        print("Required information not found in the PDF.")


def main():
    st.title("PDF Processor")

    # Get source folder's path as user input
    source_folder = st.text_input("Enter the path to the source folder:")

    # Get destination folder's path as user input
    # dest_folder = st.text_input("Enter the path to the destination folder:")

    # Convert to raw string to handle backslashes in Windows paths
    source_folder = rf"{source_folder}"

    # Debugging output
    print(f"Source Folder: {source_folder}")

    if st.button("Process Files"):
        
        # Ensure the source folder exists
        if not os.path.exists(source_folder):
            st.error("Error: Source folder does not exist.")
            # return

        # Iterate through all the available files in the source folder
        for filename in os.listdir(source_folder):
            # Check if the file is a .pdf
            if filename.lower().endswith(".pdf"):
                # Assign the source path
                source_path = os.path.join(source_folder, filename)
                # Call the function to extract data and create a new file in the destination folder
                extract_data_and_create(source_path, source_folder)
                st.success(f"Processed: {filename}")


if __name__ == "__main__":
    main()
import os
import shutil

def sort_images_by_keyword(source_folder, keywords_to_folders):
    """
    Sorts image files from a source folder into new folders based on keywords in their names.

    Args:
        source_folder (str): The path to the folder containing the images.
        keywords_to_folders (dict): A dictionary where keys are keywords to search for
                                    in filenames and values are the corresponding
                                    folder names for those images.
    """
    if not os.path.exists(source_folder):
        print(f"Error: The source folder '{source_folder}' does not exist.")
        return

    # Create a folder for images that don't match any keyword
    misc_folder = os.path.join(source_folder, 'Miscellaneous')
    if not os.path.exists(misc_folder):
        os.makedirs(misc_folder)
        print(f"Created folder: '{misc_folder}'")

    print(f"Scanning folder: '{source_folder}'...")

    # Iterate through all files in the source folder
    for filename in os.listdir(source_folder):
        # Construct the full path to the file
        source_path = os.path.join(source_folder, filename)

        # Skip directories, we only want to process files
        if os.path.isdir(source_path):
            continue
        
        # Assume the file won't be sorted initially
        sorted_flag = False

        # Check the filename against the defined keywords
        for keyword, folder_name in keywords_to_folders.items():
            if keyword.lower() in filename.lower():
                # Construct the full path for the destination folder
                destination_folder = os.path.join(source_folder, folder_name)

                # Create the destination folder if it doesn't exist
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                    print(f"Created folder: '{destination_folder}'")

                # Construct the full path for the destination file
                destination_path = os.path.join(destination_folder, filename)

                try:
                    # Move the file to the new folder
                    shutil.move(source_path, destination_path)
                    print(f"Moved '{filename}' to '{folder_name}' folder.")
                    sorted_flag = True
                    break  # Exit the loop once a keyword is matched
                except Exception as e:
                    print(f"Error moving file {filename}: {e}")
        
        # If no keyword was matched, move the file to the 'Miscellaneous' folder
        if not sorted_flag and os.path.isfile(source_path):
            try:
                shutil.move(source_path, os.path.join(misc_folder, filename))
                print(f"Moved '{filename}' to 'Miscellaneous' folder.")
            except Exception as e:
                print(f"Error moving file {filename} to Miscellaneous: {e}")

# --- Main execution part ---

if __name__ == "__main__":
    # --- Configuration ---
    # Set the path to the folder with your images
    # Example: C:\Users\YourUser\Desktop\MyImages
    # Use a raw string (r"...") or double backslashes ("\\")
    source_directory = r"C:/Users/QD2220/Downloads/Images_20250924_133804"

    # Define the keywords and the folders you want to create
    # The script will be case-insensitive when checking filenames
    sorting_rules = {
        "backoffice": "Back Office Images",
        "signage": "Signage Images",
        "cre": "CRE Group Photos",
        "vm": "VM Images",
        "morning": "Morning Meeting",
        "housekeeping": "Housekeeping & Guard",
        "store exterior": "Store Exterior",
        "store interior": "Store Interior",
        "branding": "Branding Checks",
        "ssk": "SSK",
        "washroom": "Washroom"
    }

    # Run the function with your specified settings
    sort_images_by_keyword(source_directory, sorting_rules)
    print("\nSorting process completed.")

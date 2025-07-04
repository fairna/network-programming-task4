import requests
import os
from html.parser import HTMLParser

# Server address being used
SERVER_ADDRESS = "http://127.0.0.1:8889"

class FileListingParser(HTMLParser):
    """Parser to handle file listing responses from server"""
    def handle_data(self, data):
        """Displays the file names from the HTML response"""
        if data.strip():
            print(f"File found: {data.strip()}")

def list_files():
    """Request and display the list of files from the server"""
    try:
        print("Retrieving file list from the server...")
        response = requests.get(f"{SERVER_ADDRESS}/list")
        
        # If the server responds with HTML content
        if response.headers.get('Content-Type') == 'text/html':
            parser = FileListingParser()
            parser.feed(response.text)
        else:
            print("Server responded with:")
            print(response.text)
            
        response.raise_for_status()  # Check for errors in status code
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while retrieving the file list: {e}")

import base64

def upload_file():
    """Uploads a file to the server using base64 encoding"""
    local_file = input("Enter the local file path to upload: ")

    if not os.path.exists(local_file):
        print(f"Local file not found: {local_file}")
        return

    try:
        with open(local_file, 'rb') as file:
            file_data = file.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')

        filename_only = os.path.basename(local_file)
        headers = {'X-File-Name': filename_only}

        print(f"Uploading {local_file} to the server in base64 format...")
        response = requests.post(
            f"{SERVER_ADDRESS}/upload",
            data=encoded_data,
            headers=headers
        )

        print(f"Server response ({response.status_code}):")
        print(response.text)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error during file upload: {e}")


def delete_file():
    """Deletes a file from the server"""
    filename = input("Enter the filename to delete from the server: ")

    try:
        print(f"Deleting file {filename} from the server...")
        response = requests.delete(f"{SERVER_ADDRESS}/delete?filename={filename}")

        print(f"Server response ({response.status_code}):")
        print(response.text)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Failed to delete the file: {e}")


def main():
    """Main menu for selecting client operations"""
    print("\nHTTP Client Menu:")
    print("1. List files on the server")
    print("2. Upload a file to the server")
    print("3. Delete a file from the server")
    print("4. Exit")

    try:
        while True:
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                list_files()
            elif choice == '2':
                upload_file()
            elif choice == '3':
                delete_file()
            elif choice == '4':
                break
            else:
                print("Invalid choice, please enter a number between 1-4.")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

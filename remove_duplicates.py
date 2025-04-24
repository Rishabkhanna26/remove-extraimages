import os
import hashlib
import shutil
from PIL import Image
import cv2
import imagehash

# Folder containing media files (Change this to your directory)
folder_path = "/home/rishab/Pictures"  # Replace with your folder path

# Store hashes of unique media files
file_hashes = {}

# Folder to move duplicates instead of deleting (optional)
duplicate_folder = os.path.join(folder_path, "Duplicates")
os.makedirs(duplicate_folder, exist_ok=True)

# Function to get perceptual hash (pHash) of an image
def get_image_hash(file_path):
    try:
        return str(imagehash.phash(Image.open(file_path)))
    except Exception as e:
        print(f"❌ Error processing image {file_path}: {e}")
        return None

# Function to extract the first video frame and generate hash
def get_video_frame_hash(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        success, frame = cap.read()
        cap.release()
        if success:
            image = Image.fromarray(frame)
            return str(imagehash.phash(image))
    except Exception as e:
        print(f"❌ Error processing video {video_path}: {e}")
    return None

# Function to get the SHA256 hash of a file (for non-image/video files)
def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to get a unique name for duplicates
def get_unique_filename(destination, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    # Generate a unique filename if one already exists
    while os.path.exists(os.path.join(destination, new_filename)):
        new_filename = f"{base} ({counter}){extension}"
        counter += 1
    
    return new_filename

# Scan all files in the folder
for root, _, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        
        # Process images (e.g., jpg, jpeg, png)
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            file_hash = get_image_hash(file_path)
            
            if file_hash:
                # Check if the hash already exists (duplicate found)
                if file_hash in file_hashes:
                    print(f"🗑️ Duplicate Image Found: {file_path} (Deleting)")
                    
                    # Get a unique filename for the duplicate
                    unique_filename = get_unique_filename(duplicate_folder, file)
                    shutil.move(file_path, os.path.join(duplicate_folder, unique_filename))  # Move duplicate to the "Duplicates" folder
                else:
                    file_hashes[file_hash] = file_path  # Store the original image

        # Process videos (e.g., mp4, avi, mov)
        elif file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            file_hash = get_video_frame_hash(file_path)

            if file_hash:
                # Check if the hash already exists (duplicate found)
                if file_hash in file_hashes:
                    print(f"🗑️ Duplicate Video Found: {file_path} (Deleting)")
                    
                    # Get a unique filename for the duplicate
                    unique_filename = get_unique_filename(duplicate_folder, file)
                    shutil.move(file_path, os.path.join(duplicate_folder, unique_filename))  # Move duplicate to the "Duplicates" folder
                else:
                    file_hashes[file_hash] = file_path  # Store the original video

        # Process non-image/video files (using SHA256)
        else:
            file_hash = get_file_hash(file_path)

            # Check if the hash already exists (duplicate found)
            if file_hash in file_hashes:
                print(f"🗑️ Duplicate File Found: {file_path} (Deleting)")
                
                # Get a unique filename for the duplicate
                unique_filename = get_unique_filename(duplicate_folder, file)
                shutil.move(file_path, os.path.join(duplicate_folder, unique_filename))  # Move duplicate to the "Duplicates" folder
            else:
                file_hashes[file_hash] = file_path  # Store the original file

print("✅ Duplicate scan & cleanup complete!")

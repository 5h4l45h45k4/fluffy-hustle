import pandas as pd
import requests
import os

def load_image_data(filename):
    # Load image data along with IDs from the CSV file
    data = pd.read_csv(filename)
    return data[['ID', 'Image_url']].values.tolist()

def download_images(image_data, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for profile_id, image_url in image_data:
        # Create a folder for each profile ID
        profile_folder = os.path.join(download_folder, str(profile_id))
        if not os.path.exists(profile_folder):
            os.makedirs(profile_folder)

        # Split image URLs by comma and download each one
        urls = image_url.split(',')
        for idx, url in enumerate(urls):
            url = url.strip()  # Clean up the URL
            if url:  # Proceed if the URL is not empty
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an error for bad responses

                    # Create a valid filename from the URL
                    image_name = f"{profile_id}_image_{idx + 1}.jpg"  # Naming format can be adjusted
                    image_path = os.path.join(profile_folder, image_name)

                    # Write the image to a file
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {image_path}")

                except Exception as e:
                    print(f"Failed to download {url}: {e}")

# Example usage
input_filename = 'escort_data.csv'
download_folder = 'downloaded_images'

# Load image data (ID and URLs) from CSV
image_data = load_image_data(input_filename)

# Download images
download_images(image_data, download_folder)

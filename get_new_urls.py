from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
import re

def scrape_data(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=False to see the browser in action
        page = browser.new_page()
        page.goto(url)

        scroll_count = 0  # Initialize the scroll counter
        max_scroll_attempts = 50  # Set a maximum number of scroll attempts
        last_height = page.evaluate("document.body.scrollHeight")

        # Scroll down until reaching the bottom of the page or exceeding max attempts
        while scroll_count < max_scroll_attempts:
            page.evaluate("window.scrollBy(0, window.innerHeight);")
            scroll_count += 1  # Increment the scroll counter
            print(f"Scrolling... Count: {scroll_count}")
            page.wait_for_timeout(2000)  # Adjust the wait time as needed

            # Check the new scroll height
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                print("Reached the bottom of the page.")
                break  # Break the loop if no new content is loaded
            last_height = new_height

        # Now scrape the content
        content = page.content()

        # Close the browser
        browser.close()

        return content

def extract_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    base_url = "https://www.sexemodel.com"  # Base URL for constructing complete links
    links = []

    # Find all <a class="showname"> elements and extract href attributes
    for a in soup.find_all('a', class_='showname', href=True):
        full_url = a['href'] if a['href'].startswith('http') else base_url + a['href']
        links.append(full_url)

    return links

def extract_ids(links):
    ids = []
    id_pattern = r'-(\d+)/'  # Regex to capture the ID between '-' and '/'

    for link in links:
        match = re.search(id_pattern, link)
        profile_id = match.group(1) if match else None  # Extract ID if found
        ids.append(profile_id)

    return ids

def save_to_csv(ids, links, filename):
    df = pd.DataFrame({'ID': ids, 'URL': links})
    # Append to CSV file without overwriting existing data
    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)

def load_existing_ids(filename):
    try:
        existing_data = pd.read_csv(filename)
        return set(existing_data['ID'].astype(str))  # Load existing IDs into a set
    except FileNotFoundError:
        return set()  # Return an empty set if the file doesn't exist

# Example usage
url = "https://www.sexemodel.com/"
filename = 'escort_url.csv'
existing_ids = load_existing_ids(filename)  # Load existing IDs from the CSV
scraped_content = scrape_data(url)
extracted_links = extract_links(scraped_content)

# Extract profile IDs from the links
extracted_ids = extract_ids(extracted_links)

# Filter out duplicates by checking against existing IDs
new_links = []
new_ids = []
for profile_id, link in zip(extracted_ids, extracted_links):
    if profile_id not in existing_ids and profile_id is not None:
        new_ids.append(profile_id)
        new_links.append(link)

# Print each new extracted link and ID to the console
for profile_id, link in zip(new_ids, new_links):
    print(f"New ID: {profile_id}, URL: {link}")

# Save the new IDs and URLs to a CSV file
if new_ids:
    save_to_csv(new_ids, new_links, filename)
    print(f"Extracted {len(new_links)} new links and appended to {filename}")
else:
    print("No new links found.")

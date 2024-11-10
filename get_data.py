from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
import re
import csv

def load_urls(filename):
    data = pd.read_csv(filename)
    return data['ID'].astype(str).tolist(), data['URL'].tolist()

def extract_name(url):
    # Extract name from URL based on the format provided
    match = re.search(r'/escort/([^-]+)-', url)
    return match.group(1) if match else None

def scrape_profile_data(url, profile_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(2000)  # Wait for content to load (adjust as needed)
        
        # Parse page content
        soup = BeautifulSoup(page.content(), 'html.parser')
        browser.close()

    # Extract profile information
    data = {'ID': profile_id, 'Name': extract_name(url)}

    # Last_seen and Date_registered
    last_login_div = soup.find('div', class_='last_login')
    if last_login_div:
        b_elements = last_login_div.find_all('b')
        data['Last_seen'] = b_elements[0].get_text(strip=True) if len(b_elements) > 0 else None
        data['Date_registered'] = b_elements[1].get_text(strip=True) if len(b_elements) > 1 else None

    # Views
    data['Total_views'] = soup.find('span', class_='views').get_text(strip=True) if soup.find('span', class_='views') else None
    data['Daily_views'] = soup.find('span', class_='daily-views').get_text(strip=True) if soup.find('span', class_='daily-views') else None
    data['Daily_unique_views'] = soup.find('span', class_='daily-unique-views').get_text(strip=True) if soup.find('span', class_='daily-unique-views') else None
    data['Followers'] = soup.find('span', class_='count').get_text(strip=True) if soup.find('span', class_='count') else None

    # Extract additional details (Sexe, Ethnicity, Nationality, Age) from <ul class="info">
    info_ul = soup.find('ul', class_='info')
    if info_ul:
        info_items = info_ul.find_all('li')
        data['Sexe'] = info_items[0].find('span', class_='content').get_text(strip=True) if len(info_items) > 0 else None
        data['Ethnicity'] = info_items[1].find('span', class_='content').get_text(strip=True) if len(info_items) > 1 else None
        data['Nationality'] = info_items[2].find('span', class_='content').get_text(strip=True) if len(info_items) > 2 else None
        data['Age'] = info_items[3].find('span', class_='content').get_text(strip=True) if len(info_items) > 3 else None

    # Languages
    languages_ul = soup.find('ul', class_='languages')
    if languages_ul:
        language_labels = [label.get_text(strip=True) for label in languages_ul.find_all('span', class_='label')]
        data['Languages'] = ', '.join(language_labels)

    # Working cities and telephone numbers
    working_cities_ul = soup.find('ul', class_='working-cities')
    if working_cities_ul:
        working_items = working_cities_ul.find_all('li')
        data['Base_city'] = working_items[0].find('span', class_='content').get_text(strip=True) if len(working_items) > 0 else None
        data['Working_city'] = ', '.join([city.get_text(strip=True) for city in working_items[1].find_all('span', class_='content')]) if len(working_items) > 1 else None

        # Telephone fields with validation
        phone_numbers = []
        for i in range(2, 7):  # Check up to the 6th <li> item
            if len(working_items) > i:
                telephone = working_items[i].find('span', class_='content').get_text(strip=True)
                # Validate phone format with optional "+" followed by digits
                phone_numbers.append(telephone if re.match(r'^\+?\d+$', telephone) else "n/a")
            else:
                phone_numbers.append("n/a")
        
        # Assign validated phone numbers to corresponding columns
        data['Telephone_1'] = phone_numbers[0]
        data['Telephone_2'] = phone_numbers[1]
        data['Telephone_3'] = phone_numbers[2]
        data['Telephone_4'] = phone_numbers[3]
        data['Telephone_5'] = phone_numbers[4]

    # About content
    about_content = soup.find('div', class_='about-content')
    data['About'] = about_content.get_text(strip=True) if about_content else None

    # Image URLs
    gallery_ul = soup.find('ul', class_='gallery-items active')
    if gallery_ul:
        image_links = [a['href'] for a in gallery_ul.find_all('a', class_='enlarge-image')]
        data['Image_url'] = ', '.join(image_links) if image_links else None

    return data

def save_to_csv(data_list, filename):
    # Create CSV file with headers based on keys from data_list
    keys = data_list[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

# Example usage
input_filename = 'escort_url.csv'
output_filename = 'escort_data.csv'
profile_ids, profile_urls = load_urls(input_filename)

# Limit to the first 10 URLs
profile_ids = profile_ids[:10]
profile_urls = profile_urls[:10]

# Collect data for each profile and save to output CSV
data_list = []
for profile_id, profile_url in zip(profile_ids, profile_urls):
    profile_data = scrape_profile_data(profile_url, profile_id)
    data_list.append(profile_data)
    print(f"Scraped data for ID {profile_id}: {profile_data}")

# Save all data to CSV
save_to_csv(data_list, output_filename)
print(f"Data saved to {output_filename}")

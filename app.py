import streamlit as st
import uuid
import time
from PIL import Image
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from pprint import pprint

import csv
import chat_gpt

def setup_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--mute-audio")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def extract_text_recursively(element):
    child_elements = element.find_elements(By.XPATH, ".//div[contains(@class, xh8yej3)]/div/div/div[2]")
    if not child_elements:
        return element.text
    return ' '.join([extract_text_recursively(child) for child in child_elements])

def extract_metadata_recursively(element):
    child_elements = element.find_elements(By.XPATH, ".//div[contains(@class, 'xeuugli x2lwn1j x78zum5 xdt5ytf')]")
    if not child_elements:
        return element.text
    return ' '.join([extract_text_recursively(child) for child in child_elements])


def scrape_facebook_ads_library(driver, page_list):
    base_url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&view_all_page_id="
    scraped_data = []

    for page_id in page_list:
        driver.get(base_url + page_id)
        SCROLL_PAUSE_TIME = 30
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, '_7jvw x2izyaf x1hq5gj4 x1d52u69')]")))
            ads = driver.find_elements(By.XPATH, "//div[contains(@class, '_7jvw x2izyaf x1hq5gj4 x1d52u69')]")
            print(len(ads))

            for ad in ads:
                ad_params = ['metadata', 'copy', 'creatives', 'framework']
                ad_data = dict.fromkeys(ad_params, None)

                metadata = extract_metadata_recursively(ad)
                ad_data['metadata'] = metadata

                try:
                    child_element_text = extract_text_recursively(ad)
                    ad_data['copy'] = "Ad: " + child_element_text
                except NoSuchElementException:
                    print("Error: Could not find the child element using any of the provided XPaths")
                    continue
                
                ad_framework = chat_gpt.analyse_copy(child_element_text)
                ad_data['framework'] = ad_framework

                img_elements = ad.find_elements(By.XPATH, ".//img[contains(@class, 'x1ll5gia x19kjcj4 xh8yej3')]")
                video_elements = ad.find_elements(By.XPATH, ".//video[@poster]")

                media_sources = []

                for img in img_elements:
                    src = img.get_attribute('src')
                    media_sources.append(src)

                for video in video_elements:
                    poster = video.get_attribute('poster')
                    media_sources.append(poster)

                ad_data['creatives'] = ', '.join(media_sources)

                scraped_data.append(ad_data)

        except TimeoutException:
            print(f"Error: Could not load ads for page {page_id}")

    return scraped_data

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def start_scraping(page_id):
    print(page_id)
    page_list = [page_id]  # Wrap the page_id in a list

    driver = setup_webdriver()
    scraped_data = scrape_facebook_ads_library(driver, page_list)

    driver.quit()
    fileUuid = uuid.uuid4()
    string_Uuid = str(fileUuid)
    csv_file_name = string_Uuid + ".csv"
    with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['metadata', 'copy', 'creatives', 'framework']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in scraped_data:
            writer.writerow(data)

        print("Data exported to " + csv_file_name)
        st.success('Your download is ready!', icon="✅")
        df = pd.read_csv("./" + csv_file_name.seek(0))
        get_csv = convert_df(df)

        st.download_button(
            "Press to Download",
            get_csv,
            "ads.csv",
            "text/csv",
            key='download-csv'
        )


def main():

    image = Image.open('page_id.png')

    st.title('Welcome to AdScraper')
    st.text('Step 1: Input the page ID in the form below, click Scrape and let it run!')
    user_input = st.text_input('Enter Page ID')
    submit_button = st.button('Scrape')

    if submit_button:
        start_scraping(user_input)
        st.text('Starting...')

    st.text('Step 2: Wait for your download to become available...')

    st.subheader('PLEASE NOTE:')
    st.markdown('- If the ad contents are for 18+, this scraper will NOT WORK (fb needs to check age)')
    st.markdown('- The more ads there are, the longer it will take to complete')
    st.markdown('- This demo is just a personal project / taster of what is possible, if you find this valuable, let me know and I will consider making this into a real product.')

    st.subheader('How to find the Facebook Page ID:')
    st.markdown('- Go to facebook.com/ads/library')
    st.markdown('- Find and load the page you want to use')
    st.markdown('- in the URL bar, look for page_id=[whatever number]')
    st.image(image, caption='How to get Page ID')
    st.markdown('- Copy that page iD and paste it in the box above!')

if __name__ == "__main__":
    main()


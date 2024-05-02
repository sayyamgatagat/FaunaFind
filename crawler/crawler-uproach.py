import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

def fetch_images(category_url, category_name, limit=100):
    response = requests.get(category_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    item_links = soup.find_all('a', href=True, title=True)[:limit]
    item_data = []

    base_url = urllib.parse.urlparse(category_url).scheme + '://' + urllib.parse.urlparse(category_url).netloc

    for link in item_links:
        item_url = urllib.parse.urljoin(base_url, link['href'])
        item_response = requests.get(item_url)
        item_soup = BeautifulSoup(item_response.content, 'html.parser')
        image_tags = item_soup.find_all('img')

        for img_tag in image_tags:
            image_url = urllib.parse.urljoin(base_url, img_tag['src'])
            alt_text = img_tag.get('alt', '')
            title = img_tag.get('title', '')

            item_data.append({
                'image_url': image_url,
                'page_url': item_url,
                'alt_text': alt_text,
                'title': title,
                'category': category_name,
            })

    return item_data

if __name__ == '__main__':
    category_name = input("Enter the category name: ")
    category_url = input("Enter the category URL: ")
    limit = int(input("Enter the number of images to fetch: "))

    item_images_data = fetch_images(category_url, category_name, limit)
    
    df = pd.DataFrame(item_images_data)
    
    df.to_csv(f'{category_name}_images_data.csv', index=False)
    
    print("CSV file generated successfully.")

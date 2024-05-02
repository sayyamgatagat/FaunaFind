import requests
import pandas as pd

def fetch_pexels_images(api_key, query, limit=100):
    page_no = 1
    base_url = f'https://api.pexels.com/v1/search?query={query}&per_page={80}'
    headers = {'Authorization': api_key}

    total_pages = (limit // 80) + 1

    image_data = []

    while page_no <= total_pages:
        response = requests.get(base_url + f'&page={page_no}', headers=headers)

        if response.status_code == 200:
            data = response.json()
            images = data.get('photos', [])

            for image in images:
                image_data.append({
                    'image_url': image['src']['original'],
                    'page_url': image['url'],
                    'alt_text': image['alt'],
                    'photographer': image['photographer']
                })

            page_no += 1
        else:
            print(f"Error fetching images. Status code: {response.status_code}")
            break

    return image_data

if __name__ == '__main__':
    api_key = input("Enter your Pexels API key: ")
    query = input("Enter your search query: ")
    limit = int(input("Enter the number of images to fetch: "))

    pexels_images_data = fetch_pexels_images(api_key, query, limit)

    if pexels_images_data:
        df = pd.DataFrame(pexels_images_data)

        df.to_csv(f'{query}_images_data.csv', index=False)

        print("CSV file generated successfully.")
    else:
        print("No images fetched.")

import requests

def generate_image(image_file_path, prompt, width=500, height=500, seed=1):
    url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&width={width}&height={height}&nologo=true"

    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(image_file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        raise Exception(f"Failed to fetch image. HTTP Status Code: {response.status_code}")

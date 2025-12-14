import urllib.parse
import requests
import random
import os

def get_pollinations_url(prompt):
    encoded = urllib.parse.quote(prompt)
    seed = random.randint(1, 99999)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&seed={seed}&model=turbo&nologo=true"

def get_user_input():
    print("Welcome to the AI-Generated Landscape & Garden Design Assistant!")
    print("Please provide the following details to generate your design.")

    style = input("Enter your desired style (e.g., modern, tropical, minimal, floral, edible garden): ")
    climate = input("Enter your local climate (e.g., temperate, arid, tropical): ")
    soil_type = input("Enter the soil type (e.g., clay, sandy, loam): ")
    space_size = input("Enter the size of the space (e.g., small backyard, large estate): ")
    budget = input("Enter your budget level (e.g., low, medium, high): ")
    maintenance = input("Enter your desired maintenance level (e.g., low, medium, high): ")

    prompt = f"A {style} garden design for a {space_size} area with {climate} climate and {soil_type} soil. The design should be suitable for a {budget} budget and {maintenance} maintenance. Include plant selections, hardscape recommendations like pathways and patios, and suggestions for irrigation and lighting. The design should be a photorealistic 3d aerial render, highly detailed."
    return prompt

# Get prompt from user
prompt = get_user_input()
print(f"Generated Prompt: {prompt}")

url = get_pollinations_url(prompt)
print(f"Testing URL: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        print("Image generated successfully!")
        
        # Create static directory if it doesn't exist
        if not os.path.exists('static'):
            os.makedirs('static')
            
        # Save the image
        # Use a more dynamic name for the image to avoid overwriting
        image_name = f"generated_image_{random.randint(1000, 9999)}.jpg"
        image_path = os.path.join('static', image_name)
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image saved to {image_path}")
        
    else:
        print("Image generation failed or not an image.")
except Exception as e:
    print(f"Error: {e}")

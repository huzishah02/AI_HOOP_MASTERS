import openai
import os
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="image_generation_debug.log", filemode="w")

# Set OpenAI API key
openai.api_key = "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"

def generate_image(prompt, output_path="generated_images/test_image.png"):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image_data = requests.get(image_url).content
        with open(output_path, 'wb') as image_file:
            image_file.write(image_data)
        return output_path
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None

    except openai.error.AuthenticationError:
        logging.error("Authentication Error: Invalid API Key.")
        print("Authentication Error: Please check your API key.")
        return None
    except openai.error.InvalidRequestError as e:
        logging.error(f"Invalid Request Error: {e}")
        print(f"Invalid Request Error: {e}")
        return None
    except requests.RequestException as e:
        logging.error(f"Request Error: {e}")
        print(f"Error downloading image.")
        return None
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        print(f"Unexpected error during image generation.")
        return None
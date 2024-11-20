import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY", "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")

def generate_feedback(analysis_data):
    try:
        if not openai.api_key:
            raise ValueError("OpenAI API key is not set. Set it using an environment variable or in the script")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated model
            messages=[
                {"role": "system", "content": "You are a basketball coach."},
                {"role": "user", "content": f"Based on the following pose analysis data, provide actionable feedback to improve shooting form:\n{analysis_data}"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    
    except openai.error.AuthenticationError:
        print("Error: Invalid OpenAI API key. Please check your API key.")
        return "Could not generate feedback due to an authentication issue."
    except openai.error.OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return "Could not generate feedback due to an API issue."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Could not generate feedback due to an unexpected issue."
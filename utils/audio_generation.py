from gtts import gTTS
import os
import logging

def generate_audio(feedback, output_path="generated_audio/feedback.mp3"):
    try:
        # Validate input
        if not feedback.strip():
            print("Error: Feedback text is empty.")
            return None

        # Convert text to speech
        tts = gTTS(text=feedback, lang='en')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure the folder exists
        tts.save(output_path)

        print(f"Audio saved to {output_path}")
        return output_path

    except gTTS.tts.gTTSError as e:
        print(f"gTTS Error: {e}")
        return None
    except OSError as e:
        print(f"File System Error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error generating audio: {e}")
        print(f"Unexpected Error: {e}")
        return None

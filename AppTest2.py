import uuid
import logging
from flask import Flask, request, jsonify, render_template, url_for
import cv2
from gtts import gTTS
import mediapipe as mp
import sys
import os

# Add the current directory to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

from text_generation import generate_feedback
from image_generation import generate_image
from audio_generation import generate_audio
from flask import send_from_directory



test_data = "Elbow is not aligned with wrist"
feedback = generate_feedback(test_data)
print("Generated Feedback:", feedback)

# Ensure necessary directories exist
os.makedirs("generated_images", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated_audio", exist_ok=True)

logging.basicConfig(level=logging.DEBUG, filename="app_debug.log")

app = Flask(__name__, template_folder='/Users/huzayfahshaikh/Downloads/AI HOOP MASTERS/templates')
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def home():
    return render_template('index.html')  # Frontend template

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files or not allowed_file(request.files['video'].filename):
        return jsonify({"error": "Invalid or missing video file."}), 400

    video = request.files['video']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(filepath)

    # Process video for feedback
    feedback = analyze_video(filepath)

    # Generate audio feedback
    try:
        audio_filename = f"{uuid.uuid4().hex}.mp3"
        audio_path = generate_audio(" ".join(feedback), f"generated_audio/{audio_filename}")
    except Exception as e:
        logging.error(f"Audio generation failed: {e}")
        audio_path = None

    # Generate visual feedback image
    try:
        image_filename = f"{uuid.uuid4().hex}.png"
        image_path = generate_image("A basketball player demonstrating proper shooting form.", f"generated_images/{image_filename}")
    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        image_path = None

    if not audio_path or not image_path:
        return jsonify({"error": "Failed to generate audio or image."}), 500
    
    audio_url = url_for('serve_audio', filename=audio_filename)
    image_url = url_for('serve_image', filename=image_filename)


    return jsonify({
        "feedback": feedback,
        "audio_feedback": audio_url,
        "generated_image": image_url
    })

@app.route('/generated_audio/<filename>')
def serve_audio(filename):
    return send_from_directory('generated_audio', filename)

@app.route('/generated_images/<filename>')
def serve_image(filename):
    return send_from_directory('generated_images', filename)

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    feedback = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # Skip frames for efficiency
        if frame_count % 5 != 0:
            continue

        # Convert to RGB for MediaPipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            # Extract landmarks
            landmarks = results.pose_landmarks.landmark
            right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

            # Feedback based on elbow alignment
            if abs(right_elbow.x - right_wrist.x) > 0.1:
                feedback.append("Keep your elbow straight during the shot.")
            if abs(right_shoulder.y - right_elbow.y) > 0.2:
                feedback.append("Lower your shooting arm for better control.")

    cap.release()

    # Return unique feedback messages
    feedback_summary = list(set(feedback))
    return feedback_summary if feedback_summary else ["Great shooting form!"]



@app.route('/generate_image', methods=['POST'])
def create_image():
    prompt = request.form.get('prompt', "A basketball player shooting with proper form, viewed from the side.")
    output_image_path = f"generated_images/{prompt.replace(' ', '_')}.png"

    result = generate_image(prompt, output_image_path)
    if result:
        return jsonify({"message": "Image generated successfully!", "image_path": output_image_path}), 200
    else:
        return jsonify({"error": "Image generation failed."}), 500

@app.route('/generate_audio', methods=['POST'])
def create_audio():
    feedback = request.form.get('feedback', "Great job! Keep practicing your basketball shot.")
    output_audio_path = f"generated_audio/{feedback[:10].replace(' ', '_')}.mp3"

    audio_file_path = generate_audio(feedback, output_audio_path)
    if audio_file_path:
        return jsonify({
            "message": "Audio generated successfully!",
            "audio_path": audio_file_path
        }), 200
    else:
        return jsonify({"error": "Audio generation failed."}), 500

def generate_audio(feedback_text, output_path="generated_audio/feedback.mp3"):
    try:
        tts = gTTS(text=feedback_text, lang='en')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure the folder exists
        tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)




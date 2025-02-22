import os
import joblib
from flask import Flask, request, jsonify
from pydub import AudioSegment
from flask_cors import CORS  

# Import your custom functions from other files
from preprocess_audio import preprocess_audio
from transcribe_audio import transcribe_audio
from textpreprocess import expand_text

app = Flask(__name__)
CORS(app) 

# Load your trained model and vectorizer
loaded_model = joblib.load("finaltrainmodel.pkl")
loaded_vectorizer = joblib.load("vectorizer.pkl")


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    audio_path = f"temp_audio.{file.filename.split('.')[-1]}"
    file.save(audio_path)
    cleaned_audio_path = preprocess_audio(audio_path)
    
    text = transcribe_audio(cleaned_audio_path)
    print(text)
    final_text = expand_text(text)
    print(final_text)
    
    os.remove(audio_path)
    os.remove(cleaned_audio_path)
    
    # Check if transcription failed
    if text in ["Could not understand audio", "Speech Recognition API unavailable"]:
        return jsonify({"error": text}), 400
    
    # Vectorize the transcribed text and predict with the loaded model
    text_vectorized = loaded_vectorizer.transform([final_text])
    prediction = loaded_model.predict(text_vectorized)[0]

    return jsonify({"prediction": "Fraud" if prediction == 1 else "Normal", "transcription": text})

if __name__ == "__main__":
    app.run(debug=True)

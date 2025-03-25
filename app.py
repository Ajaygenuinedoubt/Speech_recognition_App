from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import speech_recognition as sr
from gtts import gTTS
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize recognizer class (for recognizing the speech)
recognizer = sr.Recognizer()

# Function to recognize speech from microphone
def recognize_speech_from_mic():
    # Capture the audio from the user's microphone
    with sr.Microphone() as source:
        print("Adjusting microphone for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)  # Reduces background noise

        print("Microphone ready! Please speak now.")
        try:
            # Listen to the speech
            audio = recognizer.listen(source, timeout=5)  # Adjust timeout based on needs
            print("Audio captured successfully! Now recognizing...")

            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            return text

        except sr.WaitTimeoutError:
            flash("Listening timed out while waiting for input. Please try again.")
        except sr.RequestError:
            flash("Could not request results from Google Web Speech API. Check your internet connection.")
        except sr.UnknownValueError:
            flash("Google Web Speech could not understand the audio. Please try again.")

    return None

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for speech recognition and downloads
@app.route('/recognize', methods=['POST'])
def recognize():
    if request.method == 'POST':
        recognized_text = recognize_speech_from_mic()

        if recognized_text:
            flash(f"Recognized Text: {recognized_text}")

            # Convert recognized text to speech (MP3)
            tts = gTTS(recognized_text)
            audio_file = io.BytesIO()
            tts.write_to_fp(audio_file)
            audio_file.seek(0)  # Reset file pointer

            # Convert text to downloadable format
            text_file = io.StringIO(recognized_text)

            # Return recognized text and audio for download on webpage
            return render_template('index.html', recognized_text=recognized_text)

    return redirect(url_for('index'))

# Route to download MP3 file
@app.route('/download_mp3')
def download_mp3():
    recognized_text = request.args.get('recognized_text')
    tts = gTTS(recognized_text)
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)  # Reset file pointer
    return send_file(audio_file, as_attachment=True, download_name="recognized_speech.mp3", mimetype="audio/mpeg")

# Route to download Text file
@app.route('/download_text')
def download_text():
    recognized_text = request.args.get('recognized_text')
    text_file = io.StringIO(recognized_text)
    text_file.seek(0)  # Reset file pointer
    return send_file(io.BytesIO(text_file.getvalue().encode()), as_attachment=True, download_name="recognized_text.txt", mimetype="text/plain")

if __name__ == '__main__':
    app.run(debug=True)

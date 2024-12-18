from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.audio import SoundLoader #TTS specific
from PIL import Image as PILImage  # Ensure you have PIL (Pillow) installed
from dotenv import load_dotenv     # Ensure you have python-dotenv installed  
from kivy.lang import Builder     # to load the proper layout file path
from kivy.core.window import Window
from kivy.config import Config

import os
import tempfile
import atexit
import requests

Config.set('input', 'wm_pen', 'disable')
Config.set('input', 'wm_touch', 'disable')

Window.clearcolor = (0.616, 0.651, 0.659, 0.8)
Window.size = (360,675)

load_dotenv()

# Load the .kv file
#Builder.load_file("main2.kv")
Builder.load_file("visionaid2.kv")

textForTTS = ""

class MainUI(BoxLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_files = []
        atexit.register(self.cleanup_temp_files)
    
    def open_camera(self, instance):
        camera = self.ids.camera
        # Toggle the camera
        if not camera.play:
            camera.play = True
            camera.opacity = 1
            self.ids.open_camera_btn.text = "Capture Image"
            Clock.schedule_once(self.capture_image, 3)  # Add a delay to capture of 3 seconds
        else:
            camera.play = False
            camera.opacity = 0
            self.ids.open_camera_btn.text = "Open Camera"

    def capture_image(self, dt):
        # Get the camera frame and display it in the Image widget
        camera = self.ids.camera
        texture = camera.texture

        if texture:
            # Convert the Kivy texture to a PIL image
            size = texture.size
            pixels = texture.pixels
            pil_image = PILImage.frombytes(mode='RGBA', size=size, data=pixels)

            # Save the PIL image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_filename = temp_file.name
                self.temp_files.append(temp_filename)
                pil_image.save(temp_filename, format='PNG')  # Can also use 'JPEG' if desired
                print(f"Image saved to temporary file: {temp_filename}")
                print (temp_file)
                print (self.temp_files)
            
            # Update the Image widget to display the captured texture
            self.ids.image.texture = texture
            #self.camera_button.text = "Open Camera"
            camera.opacity = 0
            camera.play = False
            self.ids.status_label.text = "Image captured"

        #### once captured, call the function to send image to Azure OCR
    
    def cleanup_temp_files(self):
        """Remove temporary files created during the app's runtime."""
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
                print(f"Removed temporary file: {temp_file}")
            except Exception as e:
                print(f"Error removing file {temp_file}: {e}")    
    
    # ADD HERE - Function that sends image to Azure OCR
    def extract_text(self, instance):
       #set the path to grab the picture file(png or jpg) from the list of temporay files using index of stored location
       if self.temp_files:
           image_path = self.temp_files[-1]
       else:
           image_path = "owl.jpg"
       #convert to binary read
       with open(image_path, "rb") as image_file:
           image_data = image_file.read()       
       
       #API credentials(key, endpoint, location) are stored in .env file
       key = os.environ['KEY']
       endpoint = os.environ['ENDPOINT']
       location = os.environ['LOCATION']

       headers = {        
           'Ocp-Apim-Subscription-key': key,
           'Ocp-Apim-Subscription-Region': location,
           'Content-Type': 'application/octet-stream'
       }

       #take temporary file of image(image_data) and send to Azure OCR (POST) to extract text (GET) thorough API HTTP
       response = requests.post(endpoint, headers=headers, data=image_data)
       global textForTTS
       if response.status_code == 200:
           result = response.json()
           extracted_text = self.parse_ocr_result(result)
           self.ids.result_label.text = extracted_text
           textForTTS = extracted_text
           (print(f"Text for speech stored as variable textforTTS: This is what the variable has stored currently {textForTTS}" ))
           self.ids.status_label.text = "Ready to speak text aloud"
       else:
           self.ids.result_label.text = "Failed to extract text."
    
    def parse_ocr_result(self,result):
        text = ""
        for region in result.get("regions", []):
            for line in region.get("lines", []):
                for word in line.get("words", []):
                    text += word["text"] + " "
                text += "\n"
        return text
    
    # ADD HERE - Function that sends text to Azure Speech
    # textforTTS is the variable that contains the text to vocalized
    def speak_text(self, instance):
        # Send the text to Azure TTS and play the response
        audio_stream = self.convert_text_to_speech(textForTTS)
        if audio_stream:
            self.play_audio(audio_stream)

    def convert_text_to_speech(self, text):
        # Prepare the request headers and body

        #TTS API credentials(key2, endpoint2) are stored in .env file
        key2 = os.environ['KEY2']
        endpoint2 = os.environ['ENDPOINT2']
        
        headers = {
            'Ocp-Apim-Subscription-Key': key2,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm'
        }
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='en-US-JennyNeural'>{text}</voice>
        </speak>
        """
        try:
            response = requests.post(endpoint2, headers=headers, data=ssml.encode('utf-8'))
            response.raise_for_status() # Raise error if request fails

            # Save the audio content to a file
            with open('tts_output.wav', 'wb') as audio_file:
                audio_file.write(response.content)

            # Play the audio file
            self.play_audio('tts_output.wav')
            self.ids.status_label.text = "Success"
        except Exception as e:
            print(f"Error: {str(e)}")
            self.ids.status_label.text = "Something went wrong."

    # ADD HERE - Function that outputs sound to speaker
    def play_audio(self, audio_file):
        sound = SoundLoader.load(audio_file)
        if sound:
            sound.play()

    def clear_fields(self, instance):
        self.ids.image.source = "default_image.png"  # Replace with your default image path
        self.ids.result_label.text = "Any text gathered for speech will be shown here."
        self.ids.status_label.text = "Welcome to VizAid"

class VizAidApp(App):    
   def build(self):          
       return MainUI() # Main layout
 
if __name__ == "__main__":
    VizAidApp().run()

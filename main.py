from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from PIL import Image as PILImage  # Ensure you have PIL (Pillow) installed
from dotenv import load_dotenv     # Ensure you have python-dotenv installed  

import os
import tempfile
import atexit
import requests

load_dotenv()

textForTTS = ""

class MyApp(App):
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Button to trigger text change
        self.text_button = Button(
            text="Click me!",
            font_size=24,
            size_hint=(1, 0.1)
        )
        self.text_button.bind(on_press=self.on_button_press)

        # Button to trigger text extraction
        self.extract_button = Button(
            text="Extract Text from Image",
            font_size=24,
            size_hint=(1, 0.1)
        )
        self.extract_button.bind(on_press=self.extract_text)

        self.result_label = Label(text ='ready to extract text')

        # Button to show text prepared for tts 
        self.speech_button = Button(
            text="show text gathered for speech",
            font_size=24,
            size_hint=(1, 0.1)
        )
        self.speech_button.bind(on_press=self.read_aloud)
                
        # Camera button to capture an image
        self.camera_button = Button(
            text="Open Camera",
            font_size=24,
            size_hint=(1, 0.1)
        )
        self.camera_button.bind(on_press=self.open_camera)

        # Image widget to display the captured image
        self.image = Image(size_hint=(1, 0.5))
        
        # Camera widget (initially disabled)
        self.camera = Camera(play=False, resolution=(1280, 720))
        self.camera.opacity = 0  # Hide the camera view initially

        # Add widgets to layout
        layout.add_widget(self.text_button)
        layout.add_widget(self.camera_button)
        layout.add_widget(self.image)
        layout.add_widget(self.camera)
        layout.add_widget(self.extract_button)
        layout.add_widget(self.result_label)
        layout.add_widget(self.speech_button)

        # Register the cleanup function
        self.temp_files = []
        atexit.register(self.cleanup_temp_files)

        return layout

    def on_button_press(self, instance):
        # Change the text of the button
        self.text_button.text = "You clicked me!"

    def open_camera(self, instance):
        # Toggle the camera
        if not self.camera.play:
            self.camera.play = True
            self.camera.opacity = 1
            self.camera_button.text = "Capture Image"
            Clock.schedule_once(self.capture_image, 3)  # Add a delay to capture of 3 seconds
        else:
            self.camera.play = False
            self.camera.opacity = 0
            self.camera_button.text = "Open Camera"

    def capture_image(self, dt):
        # Get the camera frame and display it in the Image widget
        texture = self.camera.texture

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
            self.image.texture = texture
            self.camera_button.text = "Open Camera"
            self.camera.opacity = 0
            self.camera.play = False
    
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
       image_path = self.temp_files[-1]
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
           self.result_label.text = extracted_text
           textForTTS = extracted_text
           (print(f"Text for speech stored as variable textforTTS: This is what the variable has stored currently {textForTTS}" ))
       else:
           self.result_label.text = "Failed to extract text."
    
    def parse_ocr_result(self,result):
        text = ""
        for region in result.get("regions", []):
            for line in region.get("lines", []):
                for word in line.get("words", []):
                    text += word["text"] + " "
                text += "\n"
        return text
    
    def read_aloud (self, instance):
        # display text to be read from extraction
        self.speech_button.text = textForTTS

    # ADD HERE - Function that sends text to Azure Speech
    # textforTTS is the variable that contains the text to vocalized
    

    # ADD HERE - Function that outputs sound to speaker


if __name__ == "__main__":
    MyApp().run()

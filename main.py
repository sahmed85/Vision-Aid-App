from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from PIL import Image as PILImage  # Ensure you have PIL (Pillow) installed

import os
import tempfile
import atexit


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

    # ADD HERE - Function that sends text to Azure Speech

    # ADD HERE - Function that outputs sound to speaker


if __name__ == "__main__":
    MyApp().run()

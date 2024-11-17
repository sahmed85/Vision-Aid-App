# Vision-Aid-App
Implement reading assistance for images into a mobile App.

Kivy is specifically designed to create cross-platform applications, and the code you've written is suitable for both desktop and mobile environments. Here’s how you can prepare your app for mobile deployment:

### 1. **Running on local machine*

Install everything from requirments.txt file. ```pip install -r requirements.txt```

Then run the app:

```python vizaid.apy```

### 2. **Packaging for Android**
To package your Kivy app for Android, you can use **Buildozer**, which is a tool that automates the process of packaging Kivy applications. Here’s a brief overview of the steps:

- **Install Buildozer**:
  You can install Buildozer on your Linux environment (or through Windows Subsystem for Linux if you are on Windows). Use the following commands:
  ```bash
  sudo apt install -y python3-pip python3-setuptools python3-wheel
  pip install buildozer
  ```

- **Initialize Buildozer**:
  Navigate to your project directory and run:
  ```bash
  buildozer init
  ```

- **Configure Buildozer**:
  Modify the `buildozer.spec` file generated in your project directory. You can set the app name, package name, version, and permissions (e.g., camera access).

- **Build the APK**:
  To build the APK, run:
  ```bash
  buildozer -v android debug
  ```

- **Deploy to Device**:
  Connect your Android device and run:
  ```bash
  buildozer android deploy run
  ```

### 3. **Packaging for iOS**
For iOS, the process is slightly different and requires a macOS environment:

- **Install Xcode**: You need Xcode installed to create iOS apps.
  
- **Use Xcode and Kivy-ios**: You can use the Kivy-iOS toolchain to package your app:
  - Clone the Kivy-ios repository and create a project using:
    ```bash
    python3 toolchain.py create <app_name> <source_directory>
    ```
  - You can then build the project and open it in Xcode to deploy on your iOS device.

### 4. **Considerations for Mobile Deployment**
- **Permissions**: Ensure your `buildozer.spec` file includes permissions for camera access (`android.permission.CAMERA`).
- **Testing**: Test your app thoroughly on real devices to ensure all functionalities work as expected, including camera access and image saving.
- **Performance**: Mobile devices may have different performance characteristics compared to desktops, so consider optimizing resource usage in your app.

### 45 **Learning Resources**
For more detailed instructions and troubleshooting, you can refer to the official Kivy documentation:
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/en/latest/)

### Conclusion
Once packaged properly using Buildozer or Kivy-iOS, the Kivy application will be functional on mobile devices, allowing you to capture images and process them as intended.
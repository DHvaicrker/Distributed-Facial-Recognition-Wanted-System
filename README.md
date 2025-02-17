# 🔍 **Facial Recognition Security System**

## 📌 **Project Overview**
This project is a **facial recognition security system** designed to identify wanted individuals using real-time camera footage. The system utilizes a secure server-client architecture, encrypted data transmission, and an interactive GUI for seamless operation.

🖼️ **Server-Side GUI:**  
![Server-Side GUI](WorldGUI.jpg)  

---

## 🛠 **Technologies & Libraries Used**
### **🖥 Programming Language:**
- **Python 3.8 (64-bit)** – Chosen for its extensive built-in libraries, reducing the need to implement everything from scratch.

### **📚 Key Libraries:**
| Library | Purpose |
|---------|---------|
| **OpenCV** | Capturing and processing video from a camera 🎥 |
| **Facial_recognition** | Identifying faces in the video feed 🧑‍💻 |
| **Kivy & KivyMD** | GUI framework for an interactive interface 🖥️ |
| **SQLite3** | Database management for storing user and suspect data 📊 |
| **SSL** | Secure TLS connection for encrypted communication 🔒 |
| **Socket** | Enables real-time data exchange over the internet 🌐 |
| **Threading** | Runs background processes efficiently 🏃‍♂️ |
| **Pickle** | Serializes data for seamless socket transmission 📦 |
| **OS** | Handles file deletion and system interactions 🗑️ |
| **Hashlib** | Encrypts passwords for database security 🔐 |
| **Time** | Adds delays for controlled execution ⏳ |
| **NumPy** | Optimizes face recognition calculations 🔢 |
| **Captcha_image** | Generates CAPTCHA images for security 🛡️ |
| **Random** | Creates unique IDs and CAPTCHA texts 🎲 |
| **Pyttsx3** | Converts text to speech for announcements 🔊 |
| **Geopy (Nominatim)** | Determines camera location coordinates 🗺️ |

---

## 🔑 **Security Features**
- **TLS Encryption** – Secure client-server communication prevents **MITM attacks**.
- **SQL Injection Prevention** – Uses **prepared statements** to separate user input from SQL commands.
- **Brute-Force Protection** – Limits login attempts and implements CAPTCHA verification.
- **DDoS Mitigation** – Throttles new user account creation to prevent database flooding.
- **Local & Server-Side Storage** – Suspect images and login credentials are stored securely.

🖼️ **Add Wanted Person Page:**  
![Add Wanted Person](WantedPage.jpg)  

---

## 📁 **Database Structure**
The system utilizes **two SQLite databases:**
1. **Wanted Persons Database** – Stores facial images and names of suspects.
2. **User Credentials Database** – Manages login credentials with encrypted passwords.

---

## 📡 **How It Works**
1. The **server** stores a database of wanted persons and manages real-time alerts.
2. The **client** captures video footage and detects faces.
3. If a match is found, the system:
   - Alerts the user via text-to-speech.
   - Displays suspect details on the GUI.
   - Logs the detection event securely.
4. All communication is securely **encrypted using TLS**.

---

🖼️ **Live Camera Feed with Map Integration:**  
![Criminal Detection Map](criminalIMG.jpg)  


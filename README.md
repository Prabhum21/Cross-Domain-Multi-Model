# 🌌 Cross-Domain Multi-Model AI Platform

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-0078D4?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)

A cutting-edge, production-grade computer vision suite leveraging **State-of-the-Art (SOTA)** AI models to bridge the gap between human interaction and digital interfaces. This project integrates multiple AI domains—including pose estimation, facial landmarking, and hand tracking—into a unified platform for fitness, accessibility, and productivity.

---

## 🚀 Key Modules & Features

The platform is divided into two primary environments:

### 🔬 [Main 1] Real-Time Tracking Foundation
A modular tracking core designed for low-latency observation and analysis.
- **Face Mesh:** 468+ 3D facial landmarks for high-fidelity expression tracking.
- **Body Posture:** Full-body skeleton tracking for kinetic analysis.
- **Hand Tracking:** Multi-hand landmark detection for interaction modeling.
- **Iris Tracking:** Precise eye-center and iris boundary detection for gaze research.

### 🎮 [Main 2] NexGen Vision Hub
Integrated AI applications for real-world utility and Human-Computer Interaction (HCI).
- **💪 AI Fitness Coach:** Real-time rep counting for Squats, Pushups, and Jumping Jacks with form validation.
- **👀 Gaze Control:** Browser navigation (tab switching, scrolling) via eye movement.
- **✋ Gesture OS Control:** System-level commands (Volume, Fullscreen, Media, Screenshots) using hand gestures.
- **🖱️ Virtual Mouse:** High-precision cursor movement and click simulation using finger-pinch mechanics.
- **🔠 Sign Language Recognition:** Real-time translation of hand gestures into text labels.
- **🧠 Mental Health Assistant:** Real-time emotion detection (Happy, Sad, Angry, etc.) based on facial geometry.

---

## 🛠️ Technical Architecture

The project utilizes a split-microservice approach (simulated via dual Flask apps) to separate core tracking from complex application logic.

- **Frontend:** Responsive HTML5/CSS3 with Vanilla JS for real-time video streaming (MJPEG).
- **Backend:** Flask (Python) with custom multi-threading for camera management and subprocess handling.
- **AI Engine:** MediaPipe for optimized CPU-based inference and OpenCV for image processing.
- **Interaction Layer:** PyAutoGUI for system-level automation and OS hooks.

---

## 📸 Project Screenshots

| Virtual Mouse & HCI | AI Fitness Tracking |
|:---:|:---:|
| ![Virtual Mouse](main%202/gesture_screenshot.png) | ![Fitness Coach](main%201/static/screenshot.png) |

---

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/Prabhum21/Cross-Domain-Multi-Model.git
cd Cross-Domain-Multi-Model

# Install dependencies for Main 1
cd "main 1"
pip install -r requirements.txt

# Install dependencies for Main 2
cd "../main 2"
pip install flask mediapipe opencv-python pyautogui numpy
```

---

## 🚀 Usage

### Running the Tracking Core (Main 1)
```bash
cd "main 1"
python app.py
```
Access the dashboard at `http://localhost:5001`

### Running the Vision Hub (Main 2)
```bash
cd "main 2"
python app.py
```
Access the application at `http://localhost:5000`

---

## 📈 Roadmap & Future Enhancements
- [ ] **Custom Model Training:** Integrate YOLOv8 for object detection.
- [ ] **Cloud Integration:** Real-time telemetry sync to a central dashboard.
- [ ] **Mobile Support:** React Native wrapper for mobile vision capabilities.
- [ ] **Voice Integration:** Combine vision gestures with voice commands for a multimodal experience.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Developed with ❤️ for the future of AI Interaction.**

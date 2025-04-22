from flask import Flask, render_template, Response, request, jsonify
import subprocess
import cv2
import os
import logging
from threading import Lock
import signal

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables with thread safety
camera_lock = Lock()
camera = None
process = None
is_running = False

def start_tracking(script_name):
    global process, is_running
    with camera_lock:
        if not is_running:
            try:
                process = subprocess.Popen(["python", f"scripts/{script_name}"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                is_running = True
                logger.info(f"Started tracking process: {script_name}")
                return True, f"Started {script_name}"
            except Exception as e:
                logger.error(f"Failed to start tracking: {str(e)}")
                return False, str(e)
        return False, "Tracking already running"

def stop_tracking():
    global process, is_running
    with camera_lock:
        if is_running and process:
            try:
                os.kill(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
                logger.info("Tracking process terminated")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning("Tracking process killed forcefully")
            finally:
                process = None
                is_running = False
            return True, "Tracking stopped"
        return False, "No tracking process running"

def initialize_camera():
    global camera
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                logger.error("Failed to initialize camera")
                return False, "Failed to initialize camera"
            logger.info("Camera initialized successfully")
        return True, "Camera ready"

def release_camera():
    global camera
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None
            logger.info("Camera released")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed/<tracking_type>")
def video_feed(tracking_type):
    tracking_scripts = {
        "face_mesh": "scripts.face_mesh",
        "body_posture": "scripts.body_posture",
        "hand_tracking": "scripts.hand_tracking",
        "iris_tracking": "scripts.iris_tracking"
    }
    
    if tracking_type in tracking_scripts:
        module = __import__(tracking_scripts[tracking_type], fromlist=['generate_frames'])
        return Response(module.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return jsonify({"error": "Invalid tracking type"}), 400

@app.route("/start/<tracking_type>", methods=["GET"])
def start(tracking_type):
    scripts = {
        "face_mesh": "face_mesh.py",
        "body_posture": "body_posture.py",
        "hand_tracking": "hand_tracking.py",
        "iris_tracking": "iris_tracking.py"
    }
    if tracking_type in scripts:
        success, message = start_tracking(scripts[tracking_type])
        return jsonify({"success": success, "message": message}), 200 if success else 500
    return jsonify({"error": "Invalid tracking type"}), 400

@app.route("/stop", methods=["GET"])
def stop():
    success, message = stop_tracking()
    return jsonify({"success": success, "message": message}), 200 if success else 400

@app.route("/screenshot", methods=["GET"])
def screenshot():
    try:
        success, message = initialize_camera()
        if not success:
            return jsonify({"error": message}), 500

        with camera_lock:
            ret, frame = camera.read()
            if not ret:
                return jsonify({"error": "Failed to capture frame"}), 500

            screenshot_path = os.path.join("static", "screenshot.png")
            cv2.imwrite(screenshot_path, frame)
            logger.info(f"Screenshot saved at {screenshot_path}")
            return jsonify({"success": True, "message": "Screenshot captured", "path": screenshot_path}), 200
    except Exception as e:
        logger.error(f"Screenshot error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        release_camera()

@app.teardown_appcontext
def cleanup(exception):
    stop_tracking()
    release_camera()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
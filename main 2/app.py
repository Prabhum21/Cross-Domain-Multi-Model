from flask import Flask, render_template, Response, jsonify, request
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

app = Flask(__name__)

# Initialize MediaPipe components
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils  # Import mp_drawing

# Global variables for AI Fitness Coach
fitness_counter = 0
fitness_position = None
selected_exercise = "squat"

# Global variables for Gaze Control
prev_x, prev_y = 0, 0
blink_time = 0
blink_counter = 0

# Global variables for Gesture Control
action_time = 0
prev_hand_x, prev_hand_y = 0, 0

# Global variables for Virtual Mouse
alpha = 0.3  # Smoothing factor
prev_mouse_x, prev_mouse_y = 0, 0
click_time = 0
drag_active = False

# Global variables for Sign Language Recognition
gesture_text = "Waiting for gesture..."

# Initialize MediaPipe instances
pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5, max_num_hands=2)
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Screen dimensions for Virtual Mouse
screen_width, screen_height = pyautogui.size()

# ======================== AI Fitness Coach ========================
def detect_pose():
    global fitness_counter, fitness_position, selected_exercise
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            landmarks = results.pose_landmarks.landmark
            if selected_exercise == "squat":
                knee_angle = np.abs(landmarks[24].y - landmarks[26].y)  # Hip to Knee
                if knee_angle < 0.1 and fitness_position != "down":
                    fitness_position = "down"
                elif knee_angle > 0.2 and fitness_position == "down":
                    fitness_counter += 1
                    fitness_position = "up"

            elif selected_exercise == "pushup":
                elbow_angle = np.abs(landmarks[12].y - landmarks[14].y)  # Shoulder to Elbow
                if elbow_angle < 0.1 and fitness_position != "down":
                    fitness_position = "down"
                elif elbow_angle > 0.2 and fitness_position == "down":
                    fitness_counter += 1
                    fitness_position = "up"

            elif selected_exercise == "jumping_jack":
                hand_distance = np.abs(landmarks[16].x - landmarks[15].x)  # Hands apart
                if hand_distance > 0.4 and fitness_position != "up":
                    fitness_position = "up"
                elif hand_distance < 0.2 and fitness_position == "up":
                    fitness_counter += 1
                    fitness_position = "down"

        cv2.putText(frame, f"Exercise: {selected_exercise.capitalize()}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Reps: {fitness_counter}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/ai_fitness_coach')
def ai_fitness_coach():
    return render_template('ai_fitness_coach.html')

@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    global selected_exercise, fitness_counter
    selected_exercise = request.form.get('exercise')
    fitness_counter = 0  # Reset rep count when switching exercises
    return '', 204

@app.route('/ai_fitness_feed')
def ai_fitness_feed():
    return Response(detect_pose(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ======================== Gaze Control ========================
def detect_gaze():
    global prev_x, prev_y, blink_time, blink_counter
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_eye = face_landmarks.landmark[159]
                right_eye = face_landmarks.landmark[386]
                eye_center_x = (left_eye.x + right_eye.x) / 2
                eye_center_y = (left_eye.y + right_eye.y) / 2

                movement_x, movement_y = eye_center_x - prev_x, eye_center_y - prev_y
                prev_x, prev_y = eye_center_x, eye_center_y

                # Gaze-Based Navigation
                if movement_x > 0.02:
                    pyautogui.hotkey("ctrl", "tab")  # Switch to next tab
                elif movement_x < -0.02:
                    pyautogui.hotkey("ctrl", "shift", "tab")  # Switch to previous tab
                if movement_y < -0.02:
                    pyautogui.scroll(2)  # Scroll up
                elif movement_y > 0.02:
                    pyautogui.scroll(-2)  # Scroll down

                # Blink Detection for Click
                eye_distance = abs(left_eye.y - right_eye.y)
                if eye_distance < 0.01:
                    if time.time() - blink_time > 1:  # Prevent multiple clicks
                        pyautogui.click()
                        blink_counter += 1
                        blink_time = time.time()

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/gaze_control')
def gaze_control():
    return render_template('gaze_control.html')

@app.route('/gaze_feed')
def gaze_feed():
    return Response(detect_gaze(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ======================== Gesture Control ========================
def perform_action(gesture):
    global action_time
    if time.time() - action_time > 1:  # Faster reaction time
        if gesture == "swipe_right":
            pyautogui.hotkey('alt', 'tab')  # Next app
        elif gesture == "swipe_left":
            pyautogui.hotkey('alt', 'shift', 'tab')  # Previous app
        elif gesture == "swipe_up":
            pyautogui.press('volumeup')  # Increase volume
        elif gesture == "swipe_down":
            pyautogui.press('volumedown')  # Decrease volume
        elif gesture == "thumbs_up":
            pyautogui.press('playpause')  # Play/Pause
        elif gesture == "thumbs_down":
            pyautogui.press('volumemute')  # Mute/Unmute
        elif gesture == "open_hand":
            pyautogui.screenshot("gesture_screenshot.png")  # Take Screenshot
        elif gesture == "pinch":
            pyautogui.hotkey('f11')  # Toggle Fullscreen
        action_time = time.time()  # Update last action time

def detect_gestures():
    global prev_hand_x, prev_hand_y
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                index_finger = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                palm_base = hand_landmarks.landmark[0]  # Wrist base

                current_x, current_y = index_finger.x, index_finger.y
                movement_x, movement_y = current_x - prev_hand_x, current_y - prev_hand_y

                prev_hand_x, prev_hand_y = current_x, current_y  # Update previous position

                # Detect swipe gestures based on velocity
                if movement_x > 0.1:
                    perform_action("swipe_right")
                elif movement_x < -0.1:
                    perform_action("swipe_left")
                if movement_y < -0.1:
                    perform_action("swipe_up")
                elif movement_y > 0.1:
                    perform_action("swipe_down")

                # Detect thumbs up/down (relative to palm base)
                if thumb_tip.y < palm_base.y - 0.1:
                    perform_action("thumbs_up")
                elif thumb_tip.y > palm_base.y + 0.1:
                    perform_action("thumbs_down")

                # Detect open hand for screenshot
                spread_fingers = sum(1 for i in range(5, 20) if hand_landmarks.landmark[i].y < palm_base.y)
                if spread_fingers >= 4:  # 4 fingers extended
                    perform_action("open_hand")

                # Detect pinch for fullscreen
                if abs(index_finger.x - thumb_tip.x) < 0.03 and abs(index_finger.y - thumb_tip.y) < 0.03:
                    perform_action("pinch")

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/gesture_control')
def gesture_control():
    return render_template('gesture_control.html')

@app.route('/gesture_feed')
def gesture_feed():
    return Response(detect_gestures(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ======================== Virtual Mouse ========================
def generate_frames():
    global prev_mouse_x, prev_mouse_y, click_time, drag_active
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 30)  # Set high FPS for smoother video

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)  # Flip for natural movement
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger = hand_landmarks.landmark[8]  # Index Finger Tip
                thumb_tip = hand_landmarks.landmark[4]  # Thumb Tip

                # Convert normalized coordinates to screen size
                x, y = int(index_finger.x * screen_width), int(index_finger.y * screen_height)

                # Smooth cursor movement using EMA
                prev_mouse_x = int(alpha * x + (1 - alpha) * prev_mouse_x)
                prev_mouse_y = int(alpha * y + (1 - alpha) * prev_mouse_y)

                pyautogui.moveTo(prev_mouse_x, prev_mouse_y, duration=0.03)

                # Click detection (Thumb & Index close for 200ms)
                if abs(index_finger.x - thumb_tip.x) < 0.03 and abs(index_finger.y - thumb_tip.y) < 0.03:
                    if time.time() - click_time > 0.2:
                        pyautogui.click()
                        click_time = time.time()

                # Dragging (Hold fingers close for long press)
                if abs(index_finger.x - thumb_tip.x) < 0.02:
                    if not drag_active:
                        pyautogui.mouseDown()
                        drag_active = True
                else:
                    if drag_active:
                        pyautogui.mouseUp()
                        drag_active = False

        # Encode frame for low-latency streaming
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/virtual_mouse')
def virtual_mouse():
    return render_template('virtual_mouse.html')

@app.route('/virtual_mouse_feed')
def virtual_mouse_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ======================== Sign Language Recognition ========================
def detect_gesture(landmarks_list):
    if len(landmarks_list) == 1:
        landmarks = landmarks_list[0]
        
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]

        distance_thumb_index = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([index_tip.x, index_tip.y]))
        distance_pinky_wrist = np.linalg.norm(np.array([pinky_tip.x, pinky_tip.y]) - np.array([wrist.x, wrist.y]))

        if distance_thumb_index < 0.05:
            return "Fist ✊"
        elif distance_pinky_wrist > 0.25:
            return "Open Hand 🖐"
        elif thumb_tip.y < index_tip.y and thumb_tip.y < middle_tip.y:
            return "Thumbs Up 👍"
        elif index_tip.y < middle_tip.y and middle_tip.y < ring_tip.y and pinky_tip.y > ring_tip.y:
            return "Victory ✌"
        elif index_tip.y < middle_tip.y and thumb_tip.y > index_tip.y:
            return "Pointing ☝"
        elif abs(thumb_tip.x - index_tip.x) < 0.02 and abs(thumb_tip.y - index_tip.y) < 0.02:
            return "OK Sign 👌"
        elif index_tip.y < middle_tip.y and pinky_tip.y < ring_tip.y:
            return "Rock Sign 🤘"
        else:
            return "Unknown"

    elif len(landmarks_list) == 2:
        left_hand, right_hand = landmarks_list[0], landmarks_list[1]

        left_index_tip = left_hand[8]
        right_index_tip = right_hand[8]
        left_palm = left_hand[0]
        right_palm = right_hand[0]

        distance_hands = np.linalg.norm(np.array([left_palm.x, left_palm.y]) - np.array([right_palm.x, right_palm.y]))
        distance_fingers = np.linalg.norm(np.array([left_index_tip.x, left_index_tip.y]) - np.array([right_index_tip.x, right_index_tip.y]))

        if distance_fingers < 0.05:
            return "Heart Sign ❤️"
        elif distance_hands < 0.15:
            return "Clap 👏"
        elif left_palm.y < right_palm.y and right_palm.y < left_palm.y:
            return "Cross Hands ❌"
        elif left_index_tip.y < left_palm.y and right_index_tip.y < right_palm.y:
            return "Stop ✋✋"
        else:
            return "Unknown"

    return "Unknown"

def generate_sign_frames():
    global gesture_text
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            landmarks_list = [hand_landmarks.landmark for hand_landmarks in results.multi_hand_landmarks]
            gesture_text = detect_gesture(landmarks_list)

            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.putText(frame, f"Gesture: {gesture_text}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/sign_language')
def sign_language():
    return render_template('sign_language.html')

@app.route('/sign_language_feed')
def sign_language_feed():
    return Response(generate_sign_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/gesture')
def get_gesture():
    global gesture_text
    return jsonify({"gesture": gesture_text})


# ======================== Mental Health Assistant ========================

# Global variable to store the latest detected emotion
latest_emotion = "Neutral"

# Function to detect emotion based on facial landmarks
def detect_emotion(landmarks):
    """
    Improved emotion detection logic.
    """
    mouth_left = landmarks[61]  # Left mouth corner
    mouth_right = landmarks[291]  # Right mouth corner
    mouth_top = landmarks[13]  # Top lip
    mouth_bottom = landmarks[14]  # Bottom lip
    left_eye = landmarks[33]  # Left eye corner
    right_eye = landmarks[263]  # Right eye corner

    # Calculate mouth aspect ratio (MAR)
    mouth_width = abs(mouth_left.x - mouth_right.x)
    mouth_height = abs(mouth_top.y - mouth_bottom.y)
    mar = mouth_height / mouth_width if mouth_width != 0 else 0  # Avoid division by zero

    # Calculate eye aspect ratio (EAR)
    eye_width = abs(left_eye.x - right_eye.x)
    eye_height = abs(left_eye.y - right_eye.y)
    ear = eye_height / eye_width if eye_width != 0 else 0  # Avoid division by zero

    # Emotion detection logic
    if mar > 0.2:  # Smiling
        return "Happy 😊"
    elif mar < 0.1:  # Frowning
        return "Sad 😔"
    elif ear > 0.3:  # Wide eyes (surprised)
        return "Surprised 😲"
    elif mar > 0.15 and ear < 0.2:  # Angry
        return "Angry 😠"
    else:
        return "Neutral 😐"

# Function to generate frames for emotion detection
def generate_emotion_frames():
    global latest_emotion
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Error: Failed to capture image.")
            break

        # Flip the image horizontally for a natural view
        image = cv2.flip(image, 1)

        # Convert the image to RGB for MediaPipe processing
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)

        # Convert the image back to BGR for OpenCV rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw face mesh
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(200, 200, 200), thickness=1)
                )

                # Detect emotion
                landmarks = face_landmarks.landmark
                latest_emotion = detect_emotion(landmarks)

        # Display detected emotion on screen
        cv2.putText(image, f"Emotion: {latest_emotion}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode the image as a JPEG and yield it for streaming
        ret, buffer = cv2.imencode('.jpg', image)
        if not ret:
            print("Error: Failed to encode image.")
            break
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Release resources
    cap.release()
    face_mesh.close()

# Flask Routes for Mental Health Assistant
@app.route('/mental_health')
def mental_health():
    return render_template('mental_health.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_emotion_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_emotion')
def get_emotion():
    global latest_emotion
    return jsonify({"emotion": latest_emotion})




# ======================== Main Route ========================
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
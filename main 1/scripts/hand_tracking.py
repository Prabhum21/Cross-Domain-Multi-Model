import cv2
import mediapipe as mp
import time
import numpy as np

def calculate_finger_status(hand_landmarks):
    # Define the indices of the finger tips and their corresponding joints
    finger_tips = [mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP, mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP,
                   mp.solutions.hands.HandLandmark.RING_FINGER_TIP, mp.solutions.hands.HandLandmark.PINKY_TIP]
    finger_joints = [mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP, mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP,
                     mp.solutions.hands.HandLandmark.RING_FINGER_PIP, mp.solutions.hands.HandLandmark.PINKY_PIP]

    finger_status = []
    for tip, joint in zip(finger_tips, finger_joints):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            finger_status.append(1)  # Finger is open
        else:
            finger_status.append(0)  # Finger is closed

    # Thumb is a bit different
    thumb_tip = mp.solutions.hands.HandLandmark.THUMB_TIP
    thumb_ip = mp.solutions.hands.HandLandmark.THUMB_IP
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_ip].x:
        finger_status.append(1)  # Thumb is open
    else:
        finger_status.append(0)  # Thumb is closed

    return finger_status

def generate_frames():
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)

    # Initialize FPS variables
    prev_time = 0
    curr_time = 0

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Convert the image to RGB and process it
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand landmarks on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=hand_landmarks,
                    connections=mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2)
                )

                # Display handedness (left or right hand)
                hand_label = handedness.classification[0].label
                hand_score = handedness.classification[0].score
                cv2.putText(image, f'{hand_label} ({hand_score:.2f})', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Calculate finger status
                finger_status = calculate_finger_status(hand_landmarks)
                cv2.putText(image, f'Fingers: {finger_status}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Calculate and display FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(image, f'FPS: {int(fps)}', (10, 150), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# To use this function in a Flask app, you can do something like this:
# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
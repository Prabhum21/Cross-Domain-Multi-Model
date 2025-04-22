import cv2
import mediapipe as mp
import time
import numpy as np

def calculate_eye_aspect_ratio(eye_landmarks):
    # Calculate the Euclidean distances between the two sets of vertical eye landmarks
    A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])

    # Calculate the Euclidean distance between the horizontal eye landmarks
    C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])

    # Calculate the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

def generate_frames():
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)

    # Initialize FPS variables
    prev_time = 0
    curr_time = 0

    # Initialize eye blink detection variables
    ear_threshold = 0.2
    blink_counter = 0
    blink_detected = False

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Convert the image to RGB and process it
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image)

        # Draw the iris landmarks on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw iris landmarks
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(200, 200, 200), thickness=1)
                )

                # Extract eye landmarks for blink detection
                left_eye_landmarks = np.array([(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in [362, 385, 387, 263, 373, 380]])
                right_eye_landmarks = np.array([(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in [33, 160, 158, 133, 153, 144]])

                # Calculate eye aspect ratio for both eyes
                left_ear = calculate_eye_aspect_ratio(left_eye_landmarks)
                right_ear = calculate_eye_aspect_ratio(right_eye_landmarks)

                # Average the eye aspect ratio
                ear = (left_ear + right_ear) / 2.0

                # Detect eye blink
                if ear < ear_threshold:
                    if not blink_detected:
                        blink_counter += 1
                        blink_detected = True
                else:
                    blink_detected = False

                # Display blink count
                cv2.putText(image, f'Blinks: {blink_counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Calculate and display FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(image, f'FPS: {int(fps)}', (10, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

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
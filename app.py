import cv2
import mediapipe as mp
from datetime import datetime, timedelta
from collections import deque

# Load recorded video file
cap = cv2.VideoCapture("zoom1.mkv")

if not cap.isOpened():
    print("❌ Error: Could not open video file.")
    exit()

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

log_file = open("cheat_log.txt", "w")
last_face_log_time = datetime.min
log_interval = timedelta(seconds=5)

total_session_start = datetime.now()
total_gaze_violation_time = 0
total_face_absence_time = 0
cheating_start_face = None

gaze_violation_count = 0
face_absence_count = 0
head_turn_violations = 0
head_turn_frame_violations = 0

eye_movement_window = deque()
EYE_VIOLATION_THRESHOLD = 3
EYE_WINDOW_DURATION = 10

overlay_text = ""

GAZE_DRIFT_THRESHOLD = 0.03
HEAD_TURN_THRESHOLD = 0.08
HEAD_TURN_FRAME_THRESHOLD = 5

with mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb_frame)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        overlay_text = ""

        if result.multi_face_landmarks:
            for face_landmarks in result.multi_face_landmarks:
                def iris_drift(iris, inner, outer):
                    return abs((iris.x - (inner.x + outer.x) / 2) / (outer.x - inner.x + 1e-6))

                drift_left = iris_drift(face_landmarks.landmark[468], face_landmarks.landmark[133], face_landmarks.landmark[33])
                drift_right = iris_drift(face_landmarks.landmark[473], face_landmarks.landmark[362], face_landmarks.landmark[263])

                if drift_left > GAZE_DRIFT_THRESHOLD or drift_right > GAZE_DRIFT_THRESHOLD:
                    eye_movement_window.append(current_time)
                    while eye_movement_window and (current_time - eye_movement_window[0]).total_seconds() > EYE_WINDOW_DURATION:
                        eye_movement_window.popleft()
                    if len(eye_movement_window) >= EYE_VIOLATION_THRESHOLD:
                        overlay_text = "Frequent Eye Movement"
                        gaze_violation_count += 1
                        total_gaze_violation_time += 2
                        eye_movement_window.clear()
                        log_file.write(f"[{timestamp}] ALERT: Frequent eye movement detected.\n")

                nose_tip = face_landmarks.landmark[1]
                left_ear = face_landmarks.landmark[234]
                right_ear = face_landmarks.landmark[454]
                face_center_x = (left_ear.x + right_ear.x) / 2
                nose_offset = nose_tip.x - face_center_x

                if abs(nose_offset) > HEAD_TURN_THRESHOLD:
                    head_turn_frame_violations += 1
                else:
                    if head_turn_frame_violations >= HEAD_TURN_FRAME_THRESHOLD:
                        head_turn_violations += 1
                        overlay_text = "Head Turn Detected"
                        log_file.write(f"[{timestamp}] ALERT: Slight head turn detected.\n")
                    head_turn_frame_violations = 0

            if cheating_start_face:
                total_face_absence_time += (current_time - cheating_start_face).total_seconds()
                face_absence_count += 1
                cheating_start_face = None
        else:
            overlay_text = "No Face Detected"
            if (current_time - last_face_log_time) > log_interval:
                log_file.write(f"[{timestamp}] ALERT: No face detected. Possible cheating.\n")
                last_face_log_time = current_time
            if cheating_start_face is None:
                cheating_start_face = current_time

        if overlay_text:
            cv2.putText(frame, overlay_text, (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        cv2.imshow('AI Interview Monitoring Summary', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

session_end = datetime.now()
total_session_duration = (session_end - total_session_start).total_seconds()

if cheating_start_face:
    total_face_absence_time += (datetime.now() - cheating_start_face).total_seconds()
    face_absence_count += 1

log_file.close()
cap.release()
cv2.destroyAllWindows()

with open("session_summary.txt", "w") as summary:
    summary.write(f"Total Session Time: {round(total_session_duration)} seconds\n")
    summary.write(f"Eye Gaze Violations: {gaze_violation_count}\n")
    summary.write(f"Head Turn Violations: {head_turn_violations}\n")
    summary.write(f"No Face Violations: {face_absence_count}\n")
    summary.write(f"Time Not Looking at Screen: {round(total_gaze_violation_time)} sec "
                  f"({round((total_gaze_violation_time / total_session_duration) * 100, 1)}%)\n")
    summary.write(f"Time with No Face Detected: {round(total_face_absence_time)} sec "
                  f"({round((total_face_absence_time / total_session_duration) * 100, 1)}%)\n")
    total_cheating = min(total_session_duration, total_gaze_violation_time + total_face_absence_time)
    summary.write(f"Total Cheating Duration: {round(total_cheating)} sec "
                  f"({round((total_cheating / total_session_duration) * 100, 1)}%)\n")

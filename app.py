
import streamlit as st
import cv2
import mediapipe as mp
import tempfile
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Interview Monitoring Tool", layout="centered")
st.title("🎥 Hey Interviewer! Please Upload the Interview Recording")

uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "mkv", "avi"])

def analyze_video(video_path, output_dir):
    cheat_log_path = os.path.join(output_dir, "cheat_log.txt")
    session_summary_path = os.path.join(output_dir, "session_summary.txt")
    analyzed_video_path = os.path.join(output_dir, "analyzed_output.mp4")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Error: Cannot open video", None, None, None

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(analyzed_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils

    log_file = open(cheat_log_path, "w")
    total_session_start = datetime.now()
    last_face_log_time = datetime.min
    log_interval = timedelta(seconds=5)

    gaze_violation_count = 0
    face_absence_count = 0
    head_turn_violations = 0
    head_turn_frame_violations = 0

    gaze_violation_active = False
    gaze_violation_start = None
    total_gaze_violation_time = 0
    total_face_absence_time = 0
    cheating_start_face = None

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

            current_time = datetime.now()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb_frame)

            overlay_text = ""

            if result.multi_face_landmarks:
                for face_landmarks in result.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                    )

                    def iris_drift(iris, inner, outer):
                        return abs((iris.x - (inner.x + outer.x) / 2) / (outer.x - inner.x + 1e-6))

                    drift_left = iris_drift(face_landmarks.landmark[468], face_landmarks.landmark[133], face_landmarks.landmark[33])
                    drift_right = iris_drift(face_landmarks.landmark[473], face_landmarks.landmark[362], face_landmarks.landmark[263])

                    if drift_left > GAZE_DRIFT_THRESHOLD or drift_right > GAZE_DRIFT_THRESHOLD:
                        if not gaze_violation_active:
                            gaze_violation_start = current_time
                            gaze_violation_active = True
                            gaze_violation_count += 1
                        overlay_text = "Frequent Eye Movement"
                        log_file.write(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] ALERT: Eye movement detected.\n")
                    else:
                        if gaze_violation_active:
                            duration = (current_time - gaze_violation_start).total_seconds()
                            total_gaze_violation_time += duration
                            gaze_violation_active = False

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
                            log_file.write(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] ALERT: Head turn detected.\n")
                        head_turn_frame_violations = 0

                if cheating_start_face:
                    total_face_absence_time += (current_time - cheating_start_face).total_seconds()
                    face_absence_count += 1
                    cheating_start_face = None
            else:
                overlay_text = "No Face Detected"
                if (current_time - last_face_log_time) > log_interval:
                    log_file.write(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] ALERT: No face detected.\n")
                    last_face_log_time = current_time
                if cheating_start_face is None:
                    cheating_start_face = current_time

            if overlay_text:
                cv2.putText(frame, overlay_text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            out.write(frame)

    if gaze_violation_active:
        total_gaze_violation_time += (datetime.now() - gaze_violation_start).total_seconds()
    if cheating_start_face:
        total_face_absence_time += (datetime.now() - cheating_start_face).total_seconds()
        face_absence_count += 1

    total_session_duration = (datetime.now() - total_session_start).total_seconds()
    log_file.close()
    cap.release()
    out.release()

    with open(session_summary_path, "w") as summary:
        summary.write(f"Total Session Time: {round(total_session_duration)} seconds\n")
        summary.write(f"Eye Gaze Violations: {gaze_violation_count}\n")
        summary.write(f"Head Turn Violations: {head_turn_violations}\n")
        summary.write(f"No Face Violations: {face_absence_count}\n")
        summary.write(f"Time Not Looking at Screen: {round(total_gaze_violation_time)} sec "
                      f"({round((total_gaze_violation_time / total_session_duration) * 100, 1)}%)\n")
        summary.write(f"Time with No Face Detected: {round(total_face_absence_time)} sec "
                      f"({round((total_face_absence_time / total_session_duration) * 100, 1)}%)\n")
        summary.write(f"Total Cheating Duration: {round(min(total_gaze_violation_time + total_face_absence_time, total_session_duration))} sec "
                      f"({round(min(total_gaze_violation_time + total_face_absence_time, total_session_duration) / total_session_duration * 100, 1)}%)\n")

    return session_summary_path, cheat_log_path, analyzed_video_path

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_video_path = tmp_file.name

    output_dir = tempfile.mkdtemp()

    with st.spinner("Analyzing the video, please wait..."):
        summary_path, cheat_log_path, analyzed_video_path = analyze_video(temp_video_path, output_dir)

    st.success("✅ Analysis complete!")

    with open(summary_path, "r") as file:
        st.subheader("📊 Session Summary")
        st.text(file.read())

    st.subheader("📁 Download Results")
    with open(cheat_log_path, "rb") as f:
        st.download_button("Download Cheat Log", f, file_name="cheat_log.txt")

    with open(summary_path, "rb") as f:
        st.download_button("Download Session Summary", f, file_name="session_summary.txt")

    with open(analyzed_video_path, "rb") as f:
        st.download_button("Download Analyzed Video", f, file_name="analyzed_output.mp4")

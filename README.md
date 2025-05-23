
# 🎥 Interview Monitoring Tool (With UI)

## 🛡️ Overview

The **Interview Monitoring Tool** is an AI-powered Python application designed to detect cheating behavior in online or recorded interview sessions. It uses facial landmark tracking to monitor attention, presence, and suspicious actions — now with a **simple Streamlit-based web interface** for seamless video uploads and report downloads.

---

## 📌 Key Features

- ✅ **Facial Landmark Detection** using MediaPipe.
- 👁️ **Eye Gaze Drift Detection**: Identifies frequent off-screen glances.
- 🧭 **Head Turn Detection**: Flags when the interviewee turns their head.
- ❌ **Face Absence Alerts**: Logs when no face is detected in the frame.
- 📄 **Automated Cheat Log** (`cheat_log.txt`) — lists violation timestamps.
- 🧾 **Session Summary Report** (`session_summary.txt`) — detailed metrics.
- 🖥️ **Streamlit UI**: Upload video, trigger analysis, view and download reports.
- 📹 **Analyzed Video Output**: Highlights alerts visually in a downloadable video.

---

## 🧰 Requirements

Install the necessary Python packages:

```bash
pip install --upgrade pip
pip install streamlit opencv-python mediapipe
```

> If using Windows and facing permission issues, add `--user` to the command.

---

## 🚀 How to Use

1. Navigate to the folder where `interview_monitor_ui.py` is located.
2. Run the Streamlit app:

```bash
streamlit run interview_monitor_ui.py
```

3. In the browser UI:
   - Upload your recorded interview video (formats supported: `.mp4`, `.mkv`, `.avi`)
   - Wait for the analysis to complete
   - View the session summary
   - Download:
     - `cheat_log.txt`
     - `session_summary.txt`
     - `analyzed_output.mp4`

---

## 📂 Output Files

- **cheat_log.txt** — Logged alerts during the video (e.g., eye movement, face absence).
- **session_summary.txt** — Includes:
  - Total Session Time
  - Eye Gaze Violations
  - Head Turn Violations
  - No Face Detected Count
  - Time Not Looking at Screen
  - Total Cheating Duration
- **analyzed_output.mp4** — Video with overlay annotations (warnings).

---

## 📽️ Demo Video

See `Interview hack tool.mp4` included in the project for a real-world demo.

---

## 🔒 Notes

- The tool runs fully offline — no data is transmitted.
- All uploaded videos and results are stored locally and securely.
- Ideal for companies, educators, or teams conducting remote interviews.

---

## 📄 License

This project is intended for academic, research, and internal organizational use only.

---

👨‍💻 Built by **Bhanu Prasad Kandula**, 2025

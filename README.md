
# Interview Monitoring Tool

## 🛡️ Overview

The **Interview Monitoring Tool** is an AI-powered Python application designed to detect cheating behavior in online interviews or recorded interview sessions. It uses computer vision and facial landmark detection to monitor the interviewee's attention and presence.

## 📌 Key Features

- ✅ **Real-Time Facial Landmark Detection** using MediaPipe.
- 👁️ **Gaze Drift Detection**: Identifies when the interviewee frequently looks away from the screen.
- 🧭 **Head Turn Detection**: Detects if the subject turns their head away from the camera.
- ❌ **Face Absence Detection**: Alerts when no face is visible in the frame.
- 📄 **Automated Logging**: Logs all suspicious behavior in `cheat_log.txt`.
- 🧾 **Session Summary Report**: Generates a detailed summary in `session_summary.txt`.

## 🧰 Requirements

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Core Libraries:
- OpenCV
- MediaPipe
- Python Standard Libraries

## 🚀 How to Use

1. Place your recorded interview video (e.g., `zoom1.mkv`) in the project directory.
2. Run the main script:

```bash
python app.py
```

3. Press **ESC** key to stop the session and generate logs.

## 📂 Output Files

- **cheat_log.txt** — Logs of detected suspicious behavior.
- **session_summary.txt** — Summary of the interview session including:
  - Total time
  - Eye gaze violations
  - Head turn incidents
  - Time not looking at screen
  - Time with no face detected
- **Live Display** — Shows the video with overlays and detection status.

## 📽️ Demo Video

See `Interview hack tool.mp4` for a demonstration of how the tool works.

## 🔒 Notes

- This tool does not collect or transmit any data.
- All video and log files are stored locally.

## 📄 License

This project is intended for academic, research, or internal organizational use.

---

© 2025 Bhanu Prasad Kandula

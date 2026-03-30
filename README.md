# Closed-Tool-Automation-Adblocker

# Spotify-Shield-Pro 🛡️

A closed-loop ADB automation tool for real-time ad-detection and surgical playback recovery on unrooted Android devices.

---

## 🔬 The Core Logic
This project treats an Android device as an embedded system. It monitors the `MediaSession` register via ADB to detect specific metadata strings and utilizes a feedback loop to ensure the audio engine resumes correctly after a restart.

## 🚀 Features
* **Real-time Detection:** Continuously polls `dumpsys media_session` to identify ad-specific descriptions in the metadata.
* **Surgical Restart:** Leverages `am force-stop` and `am start -W` to purge the ad buffer and perform clean application transitions.
* **Closed-Loop Feedback:** Instead of using "blind" timers, the script actively polls the `PlaybackState` ($3$ = Playing, $2$ = Paused) to verify successful resumption.
* **Hardware Interrupt Simulation:** Utilizes `KEYCODE_HEADSETHOOK (79)` to bypass software-level input restrictions common in unrooted environments.

## 🧠 Challenges & Findings
* **The "Webview" Lock:** Modern browsers and WebAPKs require a "User Gesture" to unlock audio contexts. Standard virtual ADB taps are often discarded; however, hardware-level interrupts bypass this gatekeeper.
* **Xiaomi/HyperOS Specifics:** Standard ADB permissions are insufficient for UI interaction. The **USB Debugging (Security Settings)** toggle is a mandatory requirement for synthetic event injection.
* **State Machine Logic:** To prevent deadlocks, the system uses a 3-iteration "kick" loop. If the audio fails to trigger after three pulses, the system bails out to ensure the primary monitor remains active.

## 🛠️ How to Use
1.  **Phone Setup:** Enable **USB Debugging** and **USB Debugging (Security Settings)** in Developer Options.
2.  **Environment:** Install Python and `adbutils` in Termux:
    ```bash
    pip install adbutils
    ```
3.  **Bridge:** Connect via the local bridge:
    ```bash
    adb connect 127.0.0.1:5555
    ```
4.  **Execute:**
    ```bash
    python shield_v6.py
    ```

---
*Developed as a personal exploration into Android IPC and automated testing.*

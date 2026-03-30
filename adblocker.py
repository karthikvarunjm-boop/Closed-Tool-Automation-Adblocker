import adbutils
import time
import re

# --- HARDWARE CONFIGURATION ---
# Note: Using 127.0.0.1:5555 for local Termux-to-Android bridging
SERIAL = "127.0.0.1:5555"
PACKAGE = "com.spotify.music"
COMPONENT = "com.spotify.music/.MainActivity"

class SpotifyAdShield:
    """
    A closed-loop automation tool to detect ads and force-restart playback
    using hardware-level interrupts (KEYCODE_HEADSETHOOK).
    """

    def __init__(self):
        print(f"[#] Connecting to Device Serial: {SERIAL}")
        try:
            self.adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
            self.device = self.adb.device(serial=SERIAL)
            if not self.device:
                raise ConnectionError("Device not found. Ensure ADB bridge is active.")
        except Exception as e:
            print(f"[!] Init Error: {e}")
            exit(1)

    def get_playback_state(self):
        """
        Polls the Android MediaSession Service.
        Returns: 3 (Playing), 2 (Paused), or 0 (Idle/Error)
        """
        try:
            output = self.device.shell("dumpsys media_session")
            # Regex to extract the state integer from the system dump
            match = re.search(r"state=PlaybackState {state=(\d)", output)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0

    def surgical_restart(self):
        """
        Executes a forced relaunch and attempts to trigger autoplay
        via a prioritized hardware interrupt (Headset Hook 79).
        """
        print("\n[!] AD DETECTED: Initializing Surgical Restart...")
        
        # 1. Force-kill the process to clear the ad buffer
        self.device.shell(f"am force-stop {PACKAGE}")
        time.sleep(1.0)
        
        # 2. Relaunch the specific activity component
        self.device.shell(f"am start -W -n {COMPONENT}")
        
        # 3. Stabilization Buffer (Essential for low-RAM devices like Helio G85)
        print("[*] Stabilizing UI engine (7s)...")
        time.sleep(7.0) 

        # 4. The Autoplay Feedback Loop (Limited to 3 Surgical Pulses)
        print("[*] Entering Autoplay Loop (Method: KEYCODE_HEADSETHOOK)")
        for attempt in range(1, 4):
            current_state = self.get_playback_state()
            
            if current_state == 3:
                print(f"    [Attempt {attempt}/3] State: {current_state} -> SUCCESS: Music Active.")
                return # Exit back to monitor immediately
            else:
                print(f"    [Attempt {attempt}/3] State: {current_state} -> Sending Interrupt 79...")
                # KEYCODE_HEADSETHOOK (79) mimics a physical hardware button press
                self.device.shell("input keyevent 79")
                time.sleep(2.0)

        print("[-] WARNING: Autoplay failed. Resuming monitor to maintain uptime.")

    def run(self):
        print("--- Spotify Shield: Closed-Loop Monitoring Active ---")
        while True:
            try:
                # Continuous polling for the 'Advertisement' metadata tag
                system_dump = self.device.shell("dumpsys media_session")
                
                if "description=Advertisement" in system_dump or "description=Spotify" in system_dump:
                    self.surgical_restart()
                    # Prevent race conditions by adding a cooldown
                    time.sleep(5.0) 
                
                # Polling frequency
                time.sleep(2.5)
                
            except KeyboardInterrupt:
                print("\n[!] User Shutdown. Cleaning up...")
                break
            except Exception as e:
                print(f"[!] Operational Error: {e}")
                time.sleep(5.0)

if __name__ == "__main__":
    shield = SpotifyAdShield()
    shield.run()

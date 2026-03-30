import adbutils
import time
import re

# --- CONFIGURATION ---
SERIAL = "127.0.0.1:5555"
PACKAGE = "com.spotify.music"
COMPONENT = "com.spotify.music/.MainActivity"

class SpotifyShield:
    def __init__(self):
        print(f"[#] Initializing Secure Bridge on {SERIAL}...")
        self.adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
        self.device = self.adb.device(serial=SERIAL)

    def get_state(self):
        """
        Improved Logic Probe: Searches the entire dump for state indicators
        to be more resilient to different Android version outputs.
        """
        try:
            data = self.device.shell("dumpsys media_session")
            # Look for the specific PlaybackState digit
            match = re.search(r"state=PlaybackState {state=(\d)", data)
            if match:
                return int(match.group(1))
            
            # Fallback check: if the regex fails, look for raw text indicators
            if "state=3" in data or "state=PLAYING" in data.upper():
                return 3
            return 0
        except:
            return 0

    def skip_ad(self):
        print("\n[!] AD DETECTED. Executing Surgical Restart...")
        
        self.device.shell(f"am force-stop {PACKAGE}")
        time.sleep(1.5) # Increased kill buffer
        
        self.device.shell(f"am start -W -n {COMPONENT}")
        
        # Increased stabilization delay to ensure the Webview and 
        # MediaSession are fully initialized before we start probing.
        print("[*] Waiting for UI and Media Engine to stabilize...")
        time.sleep(10.0) 

        print("[>>>] Entering Autoplay Feedback Loop...")
        for attempt in range(1, 4):
            # 1. Check state BEFORE sending any signal
            state = self.get_state()
            
            if state == 3:
                print(f"      [Attempt {attempt}/3] State: {state} -> SUCCESS: Music detected.")
                return 
            
            # 2. If not playing, send the interrupt
            print(f"      [Attempt {attempt}/3] State: {state} -> Sending Interrupt 79...")
            self.device.shell("input keyevent 79")
            
            # 3. CRITICAL: Increased wait time.
            # This prevents 'double-tapping' (Play then immediate Pause).
            # It gives the MediaSessionService time to update the state to 3.
            time.sleep(4.0) 

        print("[-] NOTICE: Autoplay loop finished. Resuming background monitor.")

    def monitor(self):
        print("--- Spotify Shield: Active & Monitoring ---")
        # Ensure Termux stays awake if running in background
        self.device.shell("termux-wake-lock") 
        
        while True:
            try:
                dump = self.device.shell("dumpsys media_session")
                if "description=Advertisement" in dump or "description=Spotify" in dump:
                    self.skip_ad()
                    # Cooldown to let the new song's metadata settle
                    time.sleep(8.0) 
                
                time.sleep(3.0) # Slightly slower polling to save CPU/Battery
                
            except KeyboardInterrupt:
                self.device.shell("termux-wake-unlock")
                print("\n[!] Shield Deactivated."); break
            except Exception as e:
                print(f"[!] Comm Error: {e}"); time.sleep(5.0)

if __name__ == "__main__":
    SpotifyShield().monitor()

import subprocess
import sys
import os
import re
import time
from pathlib import Path

# -------------------- USER & PATH SETUP --------------------

HOME = Path.home()

SCRCPY_PATH = Path("scrcpy1")
FIX_SCRIPT = SCRCPY_PATH / "adb.py"
ADB_WIFI = SCRCPY_PATH / "adb-wifi.exe"

# Add scrcpy to PATH
os.environ["PATH"] = str(SCRCPY_PATH) + os.pathsep + os.environ["PATH"]
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONLEGACYWINDOWSSTDIO"] = "1"

# UTF-8 console
subprocess.run(["cmd", "/c", "chcp", "65001"], check=True)

# -------------------- AUTO-RUN fix.py --------------------

if FIX_SCRIPT.exists():
    print("Running...")
    subprocess.run([sys.executable, str(FIX_SCRIPT)], check=False)
else:
    print("⚠ fix.py not found in scrcpy1")

# -------------------- FUNCTIONS --------------------

def run(cmd):
    return subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    ).stdout

# -------------------- ADB SETUP --------------------

print("Restarting ADB...")
run(["adb", "kill-server"])
run(["adb", "disconnect"])

print("\n📡 Starting adb-wifi (scan QR on phone)...\n")
subprocess.run([str(ADB_WIFI)], encoding="utf-8", errors="ignore")

# -------------------- DEVICE DETECTION (FIXED) --------------------

print("\n⏳ Waiting for device to come online...")

device = None

for _ in range(12):  # wait up to ~12 seconds
    devices_out = run(["adb", "devices"])

    # TLS wireless debugging device ONLINE
    tls_online = re.search(
        r"(adb-[A-Za-z0-9\-]+.*?_adb-tls-connect.*?\s+device)",
        devices_out
    )

    # IP:PORT device ONLINE
    ip_online = re.search(
        r"(\d+\.\d+\.\d+\.\d+:\d+)\s+device",
        devices_out
    )

    if ip_online:
        device = ip_online.group(1)
        print(f"✔ Device found (IP): {device}")
        print(run(["adb", "connect", device]))
        break

    if tls_online:
        device = tls_online.group(1)
        print("✔ TLS Wireless Debugging device online")
        break

    time.sleep(1)

if not device:
    print("❌ Device never came online.")
    print(devices_out)
    sys.exit(1)

# -------------------- MENU --------------------

while True:
    print("\n======== MENU ========")
    print("1) scrcpy")
    print("2) adb shell")
    print("3) exit")
    choice = input("> ").strip()

    if choice == "1":
        print("\n📱 Launching scrcpy...\n")
        subprocess.Popen(["scrcpy"])
    elif choice == "2":
        subprocess.call(["adb", "shell"])
    elif choice == "3":
        sys.exit(0)
    else:
        print("Invalid choice.")

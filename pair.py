import subprocess
import sys
from pathlib import Path

# -------------------- PATHS --------------------
BASE = Path(__file__).resolve().parent
TOOLS = BASE / "scrcpy1"
FIX_SCRIPT = TOOLS / "adb.py"
ADB_EXE = TOOLS / "adb.exe"
SCRCPY_EXE = TOOLS / "scrcpy.exe"

# -------------------- RUN adb.py (fix) --------------------
if FIX_SCRIPT.exists():
    print("🔧 Running...")
    subprocess.run([sys.executable, str(FIX_SCRIPT)], check=True)
else:
    print("⚠ adb.py fix script not found in scrcpy1")

# -------------------- CHECK adb.exe --------------------
if not ADB_EXE.exists():
    print("❌ adb.exe not found in scrcpy1")
    sys.exit(1)

# -------------------- RUN adb-wifi FOR PAIRING --------------------
print("\n📡 Starting adb-wifi for pairing (scan QR on phone)...\n")
try:
    subprocess.run(["adb-wifi"], check=True)
except FileNotFoundError:
    print("❌ adb-wifi not found. Install via pip: pip install adb-wifi-py")
    sys.exit(1)

# -------------------- WAIT FOR DEVICE --------------------
def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="ignore").stdout.strip()

print("\n⏳ Waiting for device...")
device = None
for _ in range(20):
    out = run([str(ADB_EXE), "devices"])
    print(out)
    for line in out.splitlines():
        if "\tdevice" in line:
            device = line.split("\t")[0]
            break
    if device:
        break
    import time
    time.sleep(1)

if not device:
    print("❌ No device detected.")
    sys.exit(1)

print(f"\n✔ Connected device: {device}")

# -------------------- MENU --------------------
while True:
    print("\n======== MENU ========")
    print("1) scrcpy")
    print("2) adb shell")
    print("3) exit")
    choice = input("> ").strip()

    if choice == "1":
        subprocess.Popen([str(SCRCPY_EXE)])
    elif choice == "2":
        subprocess.call([str(ADB_EXE), "shell"])
    elif choice == "3":
        sys.exit(0)
    else:
        print("Invalid choice.")


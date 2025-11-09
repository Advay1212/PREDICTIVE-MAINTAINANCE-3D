#!/usr/bin/env python3
import subprocess
import sys
import time
import signal
import os

processes = []
venv_python = ".venv/bin/python3"

def cleanup(signum=None, frame=None):
    for p in processes:
        p.terminate()
    exit(0)

signal.signal(signal.SIGINT, cleanup)

print("Starting all components...")

# Start simulator
processes.append(subprocess.Popen([venv_python, "simulator.py"]))
time.sleep(2)

# Start service  
processes.append(subprocess.Popen([venv_python, "service.py"]))
time.sleep(2)

# Start dashboard
processes.append(subprocess.Popen([venv_python, "-m", "streamlit", "run", "dashboard.py", "--server.headless", "true"]))

print("All components running. Press Ctrl+C to stop.")
print("Dashboard: http://localhost:8501")
print("Simulator API: http://localhost:5000/api/v1/printer/status")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    cleanup()
#!/usr/bin/env python3
"""
System Launcher - Starts all components in the correct order
"""

import subprocess
import time
import sys
import os
import signal
import threading

class SystemLauncher:
    def __init__(self):
        self.processes = []
        
    def start_component(self, script_name, component_name, delay=0):
        if delay > 0:
            print(f"Waiting {delay} seconds before starting {component_name}...")
            time.sleep(delay)
            
        print(f"Starting {component_name}...")
        try:
            process = subprocess.Popen([sys.executable, script_name])
            self.processes.append((process, component_name))
            return process
        except Exception as e:
            print(f"Error starting {component_name}: {e}")
            return None
            
    def cleanup(self):
        print("\nShutting down all components...")
        for process, name in self.processes:
            try:
                process.terminate()
                print(f"Stopped {name}")
            except:
                pass
                
    def run(self):
        print("🖨️ 3D Printer Predictive Maintenance System")
        print("=" * 50)
        
        try:
            # Start simulator first
            self.start_component('simulator.py', 'Simulator (Flask API)')
            
            # Wait for simulator to start
            time.sleep(3)
            
            # Start service
            self.start_component('service.py', 'Predictive Maintenance Service')
            
            # Wait for service to collect some data
            time.sleep(5)
            
            print("\n" + "=" * 50)
            print("✅ All components started successfully!")
            print("\nAccess points:")
            print("- Simulator API: http://localhost:5000/api/v1/printer/status")
            print("- Dashboard: Run 'streamlit run dashboard.py' in another terminal")
            print("\nPress Ctrl+C to stop all components")
            print("=" * 50)
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.cleanup()
            print("System shutdown complete.")

if __name__ == '__main__':
    launcher = SystemLauncher()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        launcher.cleanup()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    launcher.run()
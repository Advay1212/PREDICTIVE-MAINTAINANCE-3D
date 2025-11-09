#!/usr/bin/env python3
"""
Virtual 3D Printer Simulator - Flask API
Simulates a 3D printer with various states including normal operation, errors, and anomalies.
"""

from flask import Flask, jsonify
import time
import random
import math
from datetime import datetime

app = Flask(__name__)

class PrinterSimulator:
    def __init__(self):
        self.start_time = time.time()
        self.state_cycle_duration = 60  # seconds per state
        self.states = ['idle', 'printing', 'anomaly', 'error', 'printing']
        
    def get_current_state(self):
        elapsed = time.time() - self.start_time
        cycle_position = (elapsed % (len(self.states) * self.state_cycle_duration)) / self.state_cycle_duration
        return self.states[int(cycle_position)]
    
    def get_printer_data(self):
        state = self.get_current_state()
        timestamp = datetime.now().isoformat()
        
        if state == 'idle':
            return {
                "printer_status": "idle",
                "nozzle_temp": 25.0 + random.uniform(-2, 2),
                "bed_temp": 25.0 + random.uniform(-1, 1),
                "print_progress": 0.0,
                "filament_status": "ok",
                "timestamp": timestamp
            }
        
        elif state == 'printing':
            # Normal printing with slight temperature fluctuations
            base_time = time.time() - self.start_time
            progress = (base_time % 300) / 300 * 100  # 5-minute print cycle
            
            return {
                "printer_status": "printing",
                "nozzle_temp": 210.5 + random.uniform(-1.5, 1.5),
                "bed_temp": 60.1 + random.uniform(-0.9, 0.9),
                "print_progress": min(progress, 100.0),
                "filament_status": "ok",
                "timestamp": timestamp
            }
        
        elif state == 'anomaly':
            # Overheating anomaly - temperature climbing beyond normal range
            elapsed_in_state = (time.time() - self.start_time) % self.state_cycle_duration
            temp_increase = elapsed_in_state * 0.5  # Gradual temperature increase
            
            return {
                "printer_status": "printing",  # Still printing, but anomalous
                "nozzle_temp": 210.5 + temp_increase + random.uniform(-2, 5),
                "bed_temp": 60.1 + random.uniform(-0.9, 0.9),
                "print_progress": 45.2,
                "filament_status": "ok",
                "timestamp": timestamp
            }
        
        elif state == 'error':
            return {
                "printer_status": "error",
                "nozzle_temp": 210.5 + random.uniform(-1.5, 1.5),
                "bed_temp": 60.1 + random.uniform(-0.9, 0.9),
                "print_progress": 45.2,
                "filament_status": "jammed",
                "timestamp": timestamp
            }

simulator = PrinterSimulator()

@app.route('/api/v1/printer/status')
def get_printer_status():
    return jsonify(simulator.get_printer_data())

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting 3D Printer Simulator...")
    print("API available at: http://localhost:5000/api/v1/printer/status")
    app.run(host='0.0.0.0', port=5000, debug=False)
#!/usr/bin/env python3
"""
Predictive Maintenance Service - Backend
Polls the simulator, stores data, and performs anomaly detection.
"""

import sqlite3
import requests
import json
import time
import logging
from datetime import datetime
from sklearn.ensemble import IsolationForest
import numpy as np
from collections import deque

class PredictiveMaintenanceService:
    def __init__(self):
        self.db_path = 'printer_data.db'
        self.status_file = 'status.json'
        self.alerts_log = 'alerts.log'
        self.simulator_url = 'http://localhost:5000/api/v1/printer/status'
        
        # Temperature buffer for anomaly detection
        self.temp_buffer = deque(maxlen=50)  # Last 50 readings
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.model_trained = False
        
        self.setup_database()
        self.setup_logging()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                nozzle_temp REAL,
                bed_temp REAL,
                printer_status TEXT,
                filament_status TEXT,
                print_progress REAL
            )
        ''')
        conn.commit()
        conn.close()
        
    def setup_logging(self):
        logging.basicConfig(
            filename=self.alerts_log,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def poll_simulator(self):
        try:
            response = requests.get(self.simulator_url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error polling simulator: {e}")
            return None
            
    def store_data(self, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sensor_data 
            (timestamp, nozzle_temp, bed_temp, printer_status, filament_status, print_progress)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'],
            data['nozzle_temp'],
            data['bed_temp'],
            data['printer_status'],
            data['filament_status'],
            data['print_progress']
        ))
        conn.commit()
        conn.close()
        
    def check_immediate_failures(self, data):
        alerts = []
        timestamp = data['timestamp']
        
        if data['printer_status'] == 'error':
            alert = f"Hard Failure Alert: Printer in error state at {timestamp}"
            alerts.append(alert)
            logging.error(f"HARD_FAILURE|{timestamp}|{data['printer_status']}|Printer error state")
            
        if data['filament_status'] == 'jammed':
            alert = f"Filament Jam Alert: Filament is jammed at {timestamp}"
            alerts.append(alert)
            logging.warning(f"FILAMENT_JAM|{timestamp}|{data['filament_status']}|Filament blockage")
            
        return alerts
        
    def check_predictive_anomalies(self, data):
        alerts = []
        nozzle_temp = data['nozzle_temp']
        timestamp = data['timestamp']
        
        # Add to temperature buffer
        self.temp_buffer.append(nozzle_temp)
        
        # Need at least 20 readings to start anomaly detection
        if len(self.temp_buffer) < 20:
            return alerts
            
        # Train model if not trained yet
        if not self.model_trained and len(self.temp_buffer) >= 30:
            # Use first 30 readings as "normal" baseline
            baseline_temps = list(self.temp_buffer)[:30]
            X = np.array(baseline_temps).reshape(-1, 1)
            self.isolation_forest.fit(X)
            self.model_trained = True
            print("Anomaly detection model trained")
            
        # Perform anomaly detection
        if self.model_trained:
            prediction = self.isolation_forest.predict([[nozzle_temp]])
            
            # Also check for simple temperature threshold
            temp_threshold_exceeded = nozzle_temp > 225.0  # Above normal printing temp
            
            if prediction[0] == -1 or temp_threshold_exceeded:
                alert = f"Predictive Alert: Potential Overheating Detected! Temp: {nozzle_temp:.1f}°C at {timestamp}"
                alerts.append(alert)
                logging.warning(f"PREDICTIVE_ALERT|{timestamp}|{nozzle_temp:.1f}|Overheating detected")
                
        return alerts
        
    def update_status_file(self, data, alerts):
        status = {
            "current_data": data,
            "active_alerts": alerts,
            "last_updated": datetime.now().isoformat(),
            "system_status": "error" if any("Hard Failure" in alert for alert in alerts) else 
                           "warning" if alerts else "normal"
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
            
    def run(self):
        print("Starting Predictive Maintenance Service...")
        print(f"Polling simulator every 5 seconds at {self.simulator_url}")
        
        while True:
            try:
                # Poll simulator
                data = self.poll_simulator()
                if data is None:
                    time.sleep(5)
                    continue
                    
                # Store data
                self.store_data(data)
                
                # Check for alerts
                immediate_alerts = self.check_immediate_failures(data)
                predictive_alerts = self.check_predictive_anomalies(data)
                all_alerts = immediate_alerts + predictive_alerts
                
                # Update status file
                self.update_status_file(data, all_alerts)
                
                # Print alerts to console
                for alert in all_alerts:
                    print(f"ALERT: {alert}")
                    
                print(f"Status: {data['printer_status']}, Nozzle: {data['nozzle_temp']:.1f}°C, Bed: {data['bed_temp']:.1f}°C")
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                
            time.sleep(5)

if __name__ == '__main__':
    service = PredictiveMaintenanceService()
    service.run()
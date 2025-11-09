# 3D Printer Predictive Maintenance System

A complete end-to-end predictive maintenance system for 3D printers with real-time monitoring and anomaly detection.

## Project Structure

```
carbine_phase1/
├── simulator.py      # Virtual 3D printer simulator (Flask API)
├── service.py        # Predictive maintenance backend service
├── dashboard.py      # Real-time monitoring dashboard (Streamlit)
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Components

### 1. Virtual 3D Printer Simulator (`simulator.py`)
- Flask API that simulates a 3D printer
- Cycles through different states: idle → printing → anomaly → error → printing
- Provides realistic sensor data including temperature fluctuations and anomalies
- Endpoint: `http://localhost:5000/api/v1/printer/status`

### 2. Predictive Maintenance Service (`service.py`)
- Polls the simulator every 5 seconds
- Stores historical data in SQLite database (`printer_data.db`)
- Implements rule-based alerts for immediate failures
- Uses Isolation Forest ML model for predictive anomaly detection
- Logs alerts to `alerts.log` and maintains `status.json`

### 3. Real-Time Dashboard (`dashboard.py`)
- Streamlit web interface for monitoring
- Displays current printer status and sensor readings
- Shows active alerts with color-coded severity
- Plots historical temperature trends
- Auto-refreshes every 5 seconds

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the simulator (Terminal 1):**
   ```bash
   python simulator.py
   ```

3. **Start the backend service (Terminal 2):**
   ```bash
   python service.py
   ```

4. **Start the dashboard (Terminal 3):**
   ```bash
   streamlit run dashboard.py
   ```

## Usage

1. The simulator will automatically cycle through different states every 60 seconds
2. The service will detect anomalies and log alerts
3. Access the dashboard at `http://localhost:8501` to monitor the system
4. Watch for predictive alerts when the simulator enters "anomaly" state (overheating)

## Key Features

- **Real-time monitoring** of printer status and temperatures
- **Predictive anomaly detection** using machine learning
- **Rule-based alerting** for immediate failures
- **Historical data visualization** with temperature trends
- **Self-contained system** requiring no external hardware
- **Modular architecture** with three independent components

## Alert Types

- 🔴 **Hard Failure Alert**: Printer in error state
- 🔴 **Filament Jam Alert**: Filament blockage detected  
- 🟡 **Predictive Alert**: Potential overheating detected before failure
- ✅ **Normal Status**: All systems operating normally

The system demonstrates predictive maintenance by detecting temperature anomalies before they become critical failures.
#!/usr/bin/env python3
"""
Real-Time Dashboard - Streamlit Application
Displays printer status, alerts, and historical data.
"""

import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import time

class PrinterDashboard:
    def __init__(self):
        self.db_path = 'printer_data.db'
        self.status_file = 'status.json'
        self.alerts_log = 'alerts.log'
        
    def load_current_status(self):
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Error loading status: {e}")
        return None
        
    def load_historical_data(self, minutes=10):
        try:
            if not os.path.exists(self.db_path):
                return pd.DataFrame()
                
            conn = sqlite3.connect(self.db_path)
            
            # Get data from last N minutes
            cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
            
            query = '''
                SELECT timestamp, nozzle_temp, bed_temp, printer_status
                FROM sensor_data 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 200
            '''
            
            df = pd.read_sql_query(query, conn, params=(cutoff_time,))
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
            return df
            
        except Exception as e:
            st.error(f"Error loading historical data: {e}")
            return pd.DataFrame()
            
    def load_recent_alerts(self, count=10):
        try:
            if not os.path.exists(self.alerts_log):
                return []
                
            with open(self.alerts_log, 'r') as f:
                lines = f.readlines()
                
            # Get last N lines
            recent_lines = lines[-count:] if len(lines) > count else lines
            return [line.strip() for line in recent_lines if line.strip()]
            
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
            return []

def main():
    st.set_page_config(
        page_title="3D Printer Predictive Maintenance",
        page_icon="🖨️",
        layout="wide"
    )
    
    dashboard = PrinterDashboard()
    
    # Header
    st.title("🖨️ 3D Printer Predictive Maintenance Dashboard")
    
    # Auto-refresh
    placeholder = st.empty()
    
    with placeholder.container():
        # Load current status
        status = dashboard.load_current_status()
        
        if status is None:
            st.warning("⚠️ No data available. Make sure the service is running.")
            st.stop()
            
        current_data = status.get('current_data', {})
        alerts = status.get('active_alerts', [])
        system_status = status.get('system_status', 'unknown')
        
        # Status Panel
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            printer_status = current_data.get('printer_status', 'unknown')
            if printer_status == 'printing':
                st.metric("🖨️ Printer Status", "Printing", delta="Active")
            elif printer_status == 'idle':
                st.metric("🖨️ Printer Status", "Idle", delta="Standby")
            elif printer_status == 'error':
                st.metric("🖨️ Printer Status", "Error", delta="⚠️ Issue")
            else:
                st.metric("🖨️ Printer Status", printer_status.title())
                
        with col2:
            nozzle_temp = current_data.get('nozzle_temp', 0)
            st.metric("🌡️ Nozzle Temp", f"{nozzle_temp:.1f}°C")
            
        with col3:
            bed_temp = current_data.get('bed_temp', 0)
            st.metric("🛏️ Bed Temp", f"{bed_temp:.1f}°C")
            
        with col4:
            progress = current_data.get('print_progress', 0)
            st.metric("📊 Progress", f"{progress:.1f}%")
            
        # Progress bar
        if progress > 0:
            st.progress(progress / 100.0)
            
        st.divider()
        
        # Alerts Panel
        st.subheader("🚨 Alert Status")
        
        if not alerts:
            st.info("✅ All systems normal - No active alerts")
        else:
            for alert in alerts:
                if "Hard Failure" in alert:
                    st.error(f"🔴 {alert}")
                elif "Predictive Alert" in alert:
                    st.warning(f"🟡 {alert}")
                elif "Filament Jam" in alert:
                    st.error(f"🔴 {alert}")
                else:
                    st.info(f"ℹ️ {alert}")
                    
        st.divider()
        
        # Historical Data Charts
        st.subheader("📈 Temperature Trends (Last 10 Minutes)")
        
        df = dashboard.load_historical_data(minutes=10)
        
        if df.empty:
            st.info("No historical data available yet. Wait for the service to collect data.")
        else:
            # Create temperature chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['nozzle_temp'],
                mode='lines+markers',
                name='Nozzle Temperature',
                line=dict(color='red', width=2),
                marker=dict(size=4)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['bed_temp'],
                mode='lines+markers',
                name='Bed Temperature',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ))
            
            # Add temperature thresholds
            fig.add_hline(y=225, line_dash="dash", line_color="orange", 
                         annotation_text="Overheating Threshold")
            
            fig.update_layout(
                title="Temperature Monitoring",
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        # Recent Alerts Log
        st.subheader("📋 Recent Alert History")
        recent_alerts = dashboard.load_recent_alerts(count=5)
        
        if not recent_alerts:
            st.info("No recent alerts in log file.")
        else:
            for alert in reversed(recent_alerts):  # Show newest first
                st.text(alert)
                
        # System Info
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption(f"Last Updated: {status.get('last_updated', 'Unknown')}")
            
        with col2:
            if system_status == 'normal':
                st.caption("🟢 System Status: Normal")
            elif system_status == 'warning':
                st.caption("🟡 System Status: Warning")
            elif system_status == 'error':
                st.caption("🔴 System Status: Error")
            else:
                st.caption(f"❓ System Status: {system_status}")
    
    # Auto-refresh every 5 seconds
    time.sleep(5)
    st.rerun()

if __name__ == '__main__':
    main()
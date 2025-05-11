import psutil
import time
import threading
import logging
from datetime import datetime

from app.services.anomaly import detect_anomalies, process_data

logger = logging.getLogger(__name__)

monitoring_interval = 5  
monitoring_active = True  

def get_process_info():
    """Get information about all running processes"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username', 'status']):
        try:
            process = proc.info
            
            try:
                parent_pid = proc.parent().pid if proc.parent() else None
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                parent_pid = None
                
            try:
                cmdline = ' '.join(proc.cmdline())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cmdline = ''
                
            try:
                open_files = len(proc.open_files())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                open_files = 0
                
            try:
                threads = len(proc.threads())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                threads = 0
                
            try:
                net_connections = len(proc.connections())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                net_connections = 0
                
            process_info = {
                'pid': process['pid'],
                'name': process['name'],
                'cpu_percent': round(process['cpu_percent'], 2),
                'memory_percent': round(process['memory_percent'], 2),
                'username': process['username'],
                'status': process['status'],
                'parent_pid': parent_pid,
                'is_child': parent_pid is not None,
                'cmdline': cmdline,
                'open_files': open_files,
                'threads': threads,
                'net_connections': net_connections,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            processes.append(process_info)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return processes

def monitoring_thread():
    """Background thread that monitors processes"""
    global process_data
    
    while monitoring_active:
        try:
            current_data = get_process_info()
            anomalies = detect_anomalies(current_data)
            
            process_data.update({
                'processes': current_data,
                'anomalies': anomalies,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'system': {
                    'cpu': psutil.cpu_percent(interval=None),
                    'memory': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('/').percent
                }
            })
            
            for anomaly in anomalies:
                logger.warning(f"Anomaly detected: {anomaly}")
                
            time.sleep(monitoring_interval)
        except Exception as e:
            logger.error(f"Error in monitoring thread: {e}")
            time.sleep(1)  

def start_monitoring_thread():
    """Start the monitoring thread as a daemon"""
    monitor_thread = threading.Thread(target=monitoring_thread, daemon=True)
    monitor_thread.start()
    return monitor_thread
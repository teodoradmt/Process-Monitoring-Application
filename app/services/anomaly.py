import statistics
from datetime import datetime

process_data = {}  
process_history = {}  

anomaly_thresholds = {
    'cpu': 80.0,  
    'memory': 80.0,  
    'cpu_std_dev': 2.0,  
    'memory_std_dev': 2.0  
}

def detect_anomalies(current_data):
    """Detect anomalies in process resource usage"""
    global process_history
    anomalies = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for process in current_data:
        pid = process['pid']
        
        if pid not in process_history:
            process_history[pid] = {
                'cpu': [],
                'memory': [],
                'name': process['name']
            }
        
        history = process_history[pid]
        history['cpu'].append(process['cpu_percent'])
        history['memory'].append(process['memory_percent'])
        
        if len(history['cpu']) > 10:
            history['cpu'] = history['cpu'][-10:]
            history['memory'] = history['memory'][-10:]

        if len(history['cpu']) >= 3:

            if process['cpu_percent'] > anomaly_thresholds['cpu'] or process['memory_percent'] > anomaly_thresholds['memory']:
                anomalies.append({
                    'pid': pid,
                    'name': process['name'],
                    'type': 'threshold_breach',
                    'cpu': process['cpu_percent'],
                    'memory': process['memory_percent'],
                    'timestamp': current_time
                })
            
            try:
                cpu_mean = statistics.mean(history['cpu'][:-1])  
                cpu_stdev = statistics.stdev(history['cpu'][:-1]) if len(history['cpu']) > 2 else 0
                mem_mean = statistics.mean(history['memory'][:-1])
                mem_stdev = statistics.stdev(history['memory'][:-1]) if len(history['memory']) > 2 else 0
                
                current_cpu = history['cpu'][-1]
                current_mem = history['memory'][-1]
                
                if cpu_stdev > 0 and abs(current_cpu - cpu_mean) > (anomaly_thresholds['cpu_std_dev'] * cpu_stdev):
                    anomalies.append({
                        'pid': pid,
                        'name': process['name'],
                        'type': 'cpu_spike',
                        'current': current_cpu,
                        'mean': cpu_mean,
                        'std_dev': cpu_stdev,
                        'timestamp': current_time
                    })
                    
                if mem_stdev > 0 and abs(current_mem - mem_mean) > (anomaly_thresholds['memory_std_dev'] * mem_stdev):
                    anomalies.append({
                        'pid': pid,
                        'name': process['name'],
                        'type': 'memory_spike',
                        'current': current_mem,
                        'mean': mem_mean,
                        'std_dev': mem_stdev,
                        'timestamp': current_time
                    })
            except statistics.StatisticsError:
                pass

    current_pids = {process['pid'] for process in current_data}
    for pid in list(process_history.keys()):
        if pid not in current_pids:
            del process_history[pid]
    
    return anomalies
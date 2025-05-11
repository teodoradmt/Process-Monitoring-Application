from flask import jsonify, request
from datetime import datetime
import psutil

from app.services.process import get_process_info
from app.services.anomaly import process_data

def register_routes(app):
    @app.route('/api/processes', methods=['GET'])
    def api_get_processes():
        """Get process information with optional filtering and sorting"""
        filter_name = request.args.get('name', '')
        sort_by = request.args.get('sort_by', 'pid')
        order = request.args.get('order', 'asc')
        
        data = process_data.get('processes', [])
        
        if filter_name:
            data = [p for p in data if filter_name.lower() in p['name'].lower()]
        
        if sort_by in ['pid', 'name', 'cpu_percent', 'memory_percent']:
            reverse = order.lower() == 'desc'
            data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)
        
        return jsonify({
            'processes': data,
            'total': len(data),
            'timestamp': process_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        })

    @app.route('/api/anomalies', methods=['GET'])
    def api_get_anomalies():
        """Get detected anomalies"""
        return jsonify({
            'anomalies': process_data.get('anomalies', []),
            'timestamp': process_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        })

    @app.route('/api/system', methods=['GET'])
    def api_get_system():
        """Get system resource usage"""
        return jsonify({
            'system': process_data.get('system', {
                'cpu': psutil.cpu_percent(interval=None),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent
            }),
            'timestamp': process_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        })

    @app.route('/api/process/<int:pid>', methods=['GET'])
    def api_get_process_details(pid):
        """Get detailed information about a specific process"""
        try:
            proc = psutil.Process(pid)
            
            info = proc.as_dict(attrs=['pid', 'name', 'status', 'username', 'cpu_percent', 'memory_percent', 
                                    'create_time', 'cmdline', 'cwd'])
            
            info['create_time'] = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                info['cmdline'] = ' '.join(info['cmdline'])
            except:
                info['cmdline'] = ''
                
            try:
                io = proc.io_counters()
                info['io'] = {
                    'read_bytes': io.read_bytes,
                    'write_bytes': io.write_bytes,
                    'read_count': io.read_count,
                    'write_count': io.write_count
                }
            except:
                info['io'] = {}
            
            try:
                connections = proc.connections()
                info['connections'] = len(connections)
            except:
                info['connections'] = 0
            
            try:
                mem = proc.memory_full_info()
                info['memory_details'] = {
                    'rss': mem.rss,
                    'vms': mem.vms,
                    'shared': getattr(mem, 'shared', 0),
                    'text': getattr(mem, 'text', 0),
                    'data': getattr(mem, 'data', 0)
                }
            except:
                info['memory_details'] = {}
                
            try:
                info['num_threads'] = proc.num_threads()
                info['threads'] = [{'id': t.id, 'user_time': t.user_time, 'system_time': t.system_time} 
                                for t in proc.threads()]
            except:
                info['num_threads'] = 0
                info['threads'] = []

            try:
                parent = proc.parent()
                if parent:
                    info['parent'] = {'pid': parent.pid, 'name': parent.name()}
                    info['is_child'] = True
                else:
                    info['is_child'] = False
                    info['parent'] = None
            except:
                info['is_child'] = False
                info['parent'] = None
                
            try:
                children = proc.children()
                info['children'] = [{'pid': child.pid, 'name': child.name()} for child in children]
            except:
                info['children'] = []
            
            return jsonify({
                'process': info,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        except psutil.NoSuchProcess:
            return jsonify({'error': 'Process not found'}), 404
        except psutil.AccessDenied:
            return jsonify({'error': 'Access denied to process information'}), 403
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/config', methods=['GET', 'PUT'])
    def api_config():
        """Get or update monitoring configuration"""
        from app.services.process import monitoring_interval
        from app.services.anomaly import anomaly_thresholds
        
        if request.method == 'GET':
            return jsonify({
                'monitoring_interval': monitoring_interval,
                'anomaly_thresholds': anomaly_thresholds
            })
            
        elif request.method == 'PUT':
            data = request.json
            
            if 'monitoring_interval' in data:
                try:
                    new_interval = int(data['monitoring_interval'])
                    if new_interval >= 1:
                        app.services.monitor_service.monitoring_interval = new_interval
                except (ValueError, TypeError):
                    pass
                    
            if 'anomaly_thresholds' in data:
                thresholds = data['anomaly_thresholds']
                
                if 'cpu' in thresholds:
                    try:
                        anomaly_thresholds['cpu'] = float(thresholds['cpu'])
                    except (ValueError, TypeError):
                        pass
                        
                if 'memory' in thresholds:
                    try:
                        anomaly_thresholds['memory'] = float(thresholds['memory'])
                    except (ValueError, TypeError):
                        pass
                        
                if 'cpu_std_dev' in thresholds:
                    try:
                        anomaly_thresholds['cpu_std_dev'] = float(thresholds['cpu_std_dev'])
                    except (ValueError, TypeError):
                        pass
                        
                if 'memory_std_dev' in thresholds:
                    try:
                        anomaly_thresholds['memory_std_dev'] = float(thresholds['memory_std_dev'])
                    except (ValueError, TypeError):
                        pass
            
            return jsonify({
                'monitoring_interval': monitoring_interval,
                'anomaly_thresholds': anomaly_thresholds
            })
"""
服务器状态检查工具
"""
from typing import Any, Generator
import paramiko


class CheckServerStatusTool:
    """服务器状态检查工具"""
    
    STATUS_COMMANDS = {
        'cpu_usage': "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1",
        'memory_usage': "free -m | awk 'NR==2{printf \"%.1f%%\", $3*100/$2 }'",
        'disk_usage': "df -h / | awk 'NR==2{print $5}'",
        'load_average': "uptime | awk -F'load average:' '{print $2}' | xargs",
        'uptime': "uptime -p 2>/dev/null || uptime | awk -F'up' '{print $2}' | cut -d',' -f1,2",
    }
    
    def _invoke(
        self,
        tool_parameters: dict[str, Any],
        credentials: dict[str, Any],
    ) -> Generator[dict, None, None]:
        """检查服务器状态"""
        host = tool_parameters.get('host', '')
        port = tool_parameters.get('port', 22)
        
        username = credentials.get('default_username', 'root')
        password = credentials.get('default_password', '')
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=30,
                look_for_keys=False,
                allow_agent=False,
            )
            
            status = {'online': True, 'host': host}
            
            for key, cmd in self.STATUS_COMMANDS.items():
                try:
                    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
                    result = stdout.read().decode('utf-8', errors='replace').strip()
                    status[key] = result if result else "N/A"
                except Exception:
                    status[key] = "N/A"
            
            yield status
            
        except Exception as e:
            yield {
                'online': False,
                'host': host,
                'error': str(e),
                'cpu_usage': 'N/A',
                'memory_usage': 'N/A',
                'disk_usage': 'N/A',
                'load_average': 'N/A',
                'uptime': 'N/A',
            }
        finally:
            client.close()

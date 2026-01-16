"""
SSH 服务
提供 SSH 连接和命令执行功能
"""
import paramiko
from typing import Dict, Any, Optional
from loguru import logger

from app.config import settings


class SSHConnectionError(Exception):
    """SSH 连接错误"""
    pass


class CommandExecutionError(Exception):
    """命令执行错误"""
    pass


class SSHService:
    """SSH 服务类"""
    
    def __init__(self):
        self.default_timeout = settings.SSH_TIMEOUT
    
    def _create_client(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> paramiko.SSHClient:
        """创建 SSH 客户端连接"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=self.default_timeout,
                look_for_keys=False,
                allow_agent=False,
            )
            return client
        except paramiko.AuthenticationException:
            raise SSHConnectionError(f"认证失败: {username}@{host}")
        except paramiko.SSHException as e:
            raise SSHConnectionError(f"SSH 连接错误: {str(e)}")
        except TimeoutError:
            raise SSHConnectionError(f"连接超时: {host}:{port}")
        except Exception as e:
            raise SSHConnectionError(f"连接失败: {str(e)}")
    
    def test_connection(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        password: str = "",
    ) -> bool:
        """测试 SSH 连接"""
        try:
            client = self._create_client(host, port, username, password)
            client.close()
            return True
        except SSHConnectionError:
            return False
    
    def execute_command(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        command: str,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        执行远程命令
        
        Returns:
            Dict containing stdout, stderr, exit_code
        """
        client = None
        try:
            client = self._create_client(host, port, username, password)
            
            # 执行命令
            stdin, stdout, stderr = client.exec_command(
                command,
                timeout=timeout,
            )
            
            # 获取结果
            stdout_text = stdout.read().decode('utf-8', errors='replace')
            stderr_text = stderr.read().decode('utf-8', errors='replace')
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                'stdout': stdout_text,
                'stderr': stderr_text,
                'exit_code': exit_code,
            }
            
        except SSHConnectionError:
            raise
        except Exception as e:
            logger.exception(f"命令执行失败: {command}")
            raise CommandExecutionError(f"命令执行失败: {str(e)}")
        finally:
            if client:
                client.close()
    
    def get_server_status(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        password: str = "",
    ) -> Dict[str, str]:
        """获取服务器状态摘要"""
        status = {}
        
        commands = {
            'cpu_usage': "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1",
            'memory_usage': "free -m | awk 'NR==2{printf \"%.1f%%\", $3*100/$2 }'",
            'disk_usage': "df -h / | awk 'NR==2{print $5}'",
            'load_average': "uptime | awk -F'load average:' '{print $2}' | xargs",
            'uptime': "uptime -p 2>/dev/null || uptime | awk -F'up' '{print $2}' | cut -d',' -f1,2",
        }
        
        client = None
        try:
            client = self._create_client(host, port, username, password)
            
            for key, cmd in commands.items():
                try:
                    stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
                    result = stdout.read().decode('utf-8', errors='replace').strip()
                    status[key] = result if result else "N/A"
                except Exception:
                    status[key] = "N/A"
            
            return status
            
        finally:
            if client:
                client.close()
    
    def check_service_status(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        service_name: str,
    ) -> Dict[str, Any]:
        """检查服务状态"""
        commands = {
            'systemctl': f"systemctl is-active {service_name}",
            'status': f"systemctl status {service_name} --no-pager -l",
        }
        
        results = {}
        client = None
        
        try:
            client = self._create_client(host, port, username, password)
            
            for key, cmd in commands.items():
                stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
                results[key] = {
                    'stdout': stdout.read().decode('utf-8', errors='replace'),
                    'stderr': stderr.read().decode('utf-8', errors='replace'),
                    'exit_code': stdout.channel.recv_exit_status(),
                }
            
            # 判断服务是否活跃
            is_active = results['systemctl']['stdout'].strip() == 'active'
            
            return {
                'service': service_name,
                'is_active': is_active,
                'details': results['status']['stdout'],
            }
            
        finally:
            if client:
                client.close()
    
    def get_container_status(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        container_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取 Docker 容器状态"""
        if container_name:
            cmd = f"docker ps -a --filter 'name={container_name}' --format '{{{{.ID}}}}\\t{{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}'"
        else:
            cmd = "docker ps -a --format '{{.ID}}\\t{{.Names}}\\t{{.Status}}\\t{{.Ports}}'"
        
        client = None
        try:
            client = self._create_client(host, port, username, password)
            
            stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
            output = stdout.read().decode('utf-8', errors='replace')
            error = stderr.read().decode('utf-8', errors='replace')
            
            if error:
                return {'error': error, 'containers': []}
            
            containers = []
            for line in output.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        containers.append({
                            'id': parts[0],
                            'name': parts[1],
                            'status': parts[2],
                            'ports': parts[3] if len(parts) > 3 else '',
                        })
            
            return {'containers': containers}
            
        finally:
            if client:
                client.close()
    
    def get_kubernetes_pods(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        namespace: str = "default",
    ) -> Dict[str, Any]:
        """获取 Kubernetes Pod 状态"""
        cmd = f"kubectl get pods -n {namespace} -o wide"
        
        client = None
        try:
            client = self._create_client(host, port, username, password)
            
            stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
            output = stdout.read().decode('utf-8', errors='replace')
            error = stderr.read().decode('utf-8', errors='replace')
            
            return {
                'namespace': namespace,
                'output': output,
                'error': error if error else None,
            }
            
        finally:
            if client:
                client.close()

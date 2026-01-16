"""
SSH 命令执行工具
"""
from typing import Any, Generator
import paramiko
import re


# 允许的命令前缀白名单
ALLOWED_COMMAND_PREFIXES = [
    # kubectl 命令
    "kubectl get",
    "kubectl describe",
    "kubectl logs",
    "kubectl top",
    # docker 命令
    "docker ps",
    "docker logs",
    "docker inspect",
    "docker stats",
    # 系统状态命令
    "systemctl status",
    "systemctl is-active",
    "df -h",
    "df -",
    "free -m",
    "free -",
    "top -bn1",
    "ps aux",
    "ps -",
    # 网络命令
    "netstat -tlnp",
    "netstat -",
    "ss -tlnp",
    "ss -",
    "ping ",
    "curl ",
    "wget ",
    # 日志命令
    "cat /var/log",
    "tail ",
    "head ",
    "journalctl",
    "grep ",
    # 其他安全命令
    "uptime",
    "hostname",
    "whoami",
    "date",
    "uname",
    "ip addr",
    "ip route",
    "cat /etc/hosts",
    "cat /etc/resolv.conf",
]

# 危险字符/命令
DANGEROUS_PATTERNS = [
    r';',           # 命令分隔
    r'&&',          # 命令链接
    r'\|\|',        # 命令链接
    r'\|(?!grep)',  # 管道（允许 grep）
    r'`',           # 命令替换
    r'\$\(',        # 命令替换
    r'>',           # 重定向
    r'<',           # 重定向
    r'rm\s+-rf',    # 危险删除
    r'rm\s+-r',     # 危险删除
    r'mkfs',        # 格式化
    r'dd\s+if=',    # 磁盘操作
    r'shutdown',    # 关机
    r'reboot',      # 重启
    r'init\s+0',    # 关机
    r'halt',        # 停止
    r'poweroff',    # 关机
]


def validate_command(command: str) -> tuple[bool, str]:
    """
    验证命令是否安全
    
    Returns:
        (is_valid, error_message)
    """
    command_lower = command.lower().strip()
    
    # 检查是否在白名单中
    is_allowed = any(
        command_lower.startswith(prefix.lower())
        for prefix in ALLOWED_COMMAND_PREFIXES
    )
    
    if not is_allowed:
        return False, f"命令不在允许列表中。允许的命令前缀: {', '.join(ALLOWED_COMMAND_PREFIXES[:10])}..."
    
    # 检查危险模式
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"命令包含不允许的模式"
    
    return True, ""


def validate_ip(ip: str, allowed_ranges: str = "") -> tuple[bool, str]:
    """验证 IP 地址"""
    # 基本 IP 格式验证
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, ip):
        return False, "无效的 IP 地址格式"
    
    # 验证每个数字段
    parts = ip.split('.')
    for part in parts:
        if int(part) > 255:
            return False, "无效的 IP 地址"
    
    # 如果配置了 IP 白名单，检查是否在范围内
    if allowed_ranges:
        # 这里简化处理，实际应该用 ipaddress 库检查 CIDR
        allowed_list = [r.strip() for r in allowed_ranges.split(',')]
        if ip not in allowed_list and not any(ip.startswith(r.split('/')[0].rsplit('.', 1)[0]) for r in allowed_list):
            return False, f"IP {ip} 不在允许的范围内"
    
    return True, ""


class ExecuteCommandTool:
    """SSH 命令执行工具"""
    
    def _invoke(
        self,
        tool_parameters: dict[str, Any],
        credentials: dict[str, Any],
    ) -> Generator[dict, None, None]:
        """
        执行 SSH 命令
        """
        host = tool_parameters.get('host', '')
        command = tool_parameters.get('command', '')
        port = tool_parameters.get('port', 22)
        
        username = credentials.get('default_username', 'root')
        password = credentials.get('default_password', '')
        allowed_ranges = credentials.get('allowed_ip_ranges', '')
        
        # 验证 IP
        is_valid_ip, ip_error = validate_ip(host, allowed_ranges)
        if not is_valid_ip:
            yield self._create_error_response(ip_error)
            return
        
        # 验证命令
        is_valid_cmd, cmd_error = validate_command(command)
        if not is_valid_cmd:
            yield self._create_error_response(cmd_error)
            return
        
        # 执行 SSH 命令
        try:
            result = self._execute_ssh_command(
                host=host,
                port=port,
                username=username,
                password=password,
                command=command,
            )
            yield result
            
        except Exception as e:
            yield self._create_error_response(f"执行失败: {str(e)}")
    
    def _execute_ssh_command(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        command: str,
        timeout: int = 30,
    ) -> dict:
        """执行 SSH 命令"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                look_for_keys=False,
                allow_agent=False,
            )
            
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            
            stdout_text = stdout.read().decode('utf-8', errors='replace')
            stderr_text = stderr.read().decode('utf-8', errors='replace')
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                'success': exit_code == 0,
                'stdout': stdout_text,
                'stderr': stderr_text,
                'exit_code': exit_code,
                'host': host,
                'command': command,
            }
            
        except paramiko.AuthenticationException:
            raise Exception(f"SSH 认证失败: {username}@{host}")
        except paramiko.SSHException as e:
            raise Exception(f"SSH 连接错误: {str(e)}")
        except TimeoutError:
            raise Exception(f"连接超时: {host}:{port}")
        finally:
            client.close()
    
    def _create_error_response(self, error_message: str) -> dict:
        """创建错误响应"""
        return {
            'success': False,
            'stdout': '',
            'stderr': error_message,
            'exit_code': -1,
        }

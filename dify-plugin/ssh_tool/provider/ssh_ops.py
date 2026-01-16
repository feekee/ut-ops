"""
SSH 运维工具 Provider
"""
from typing import Any


class SshOpsProvider:
    """SSH 运维工具提供者"""
    
    def validate_credentials(self, credentials: dict[str, Any]) -> None:
        """验证凭据配置"""
        if not credentials.get('default_username'):
            raise ValueError("请配置默认用户名")
        if not credentials.get('default_password'):
            raise ValueError("请配置默认密码")

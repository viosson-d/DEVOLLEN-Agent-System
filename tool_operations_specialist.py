"""
Tool Operations Specialist Agent
工具操作专家 Agent - 负责与各种工具交互，记录每次操作
"""

import os
import json
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


# ============= Agent 职能定义 =============
class ToolOperationsRole:
    """工具操作专家的职能"""
    
    TITLE = "Tool Operations Specialist"
    TITLE_CN = "工具操作专家"
    
    RESPONSIBILITIES = [
        "执行工具操作命令",
        "记录每次工具交互",
        "处理工具调用错误",
        "维护操作日志",
        "工具状态检查",
        "操作历史追溯"
    ]
    
    SKILLS = [
        "tool_invocation",          # 工具调用
        "interaction_logging",      # 交互日志
        "error_handling",           # 错误处理
        "operation_tracking",       # 操作追踪
        "retry_mechanism",          # 重试机制
        "state_management"          # 状态管理
    ]
    
    SUPPORTED_TOOLS = [
        "langfuse",         # 监控工具
        "github",           # 代码托管
        "slack",            # 沟通工具
        "jira",             # 项目管理
        "database",         # 数据库
        "api_endpoints"     # 各种 API
    ]


# ============= 数据模型 =============
class OperationType(Enum):
    """操作类型"""
    READ = "read"           # 读取操作
    WRITE = "write"         # 写入操作
    UPDATE = "update"       # 更新操作
    DELETE = "delete"       # 删除操作
    EXECUTE = "execute"     # 执行操作
    QUERY = "query"         # 查询操作


class OperationStatus(Enum):
    """操作状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class OperationRecord:
    """操作记录"""
    operation_id: str
    tool_name: str
    operation_type: OperationType
    command: str
    parameters: Dict[str, Any]
    status: OperationStatus
    request_payload: Optional[Dict] = None
    response_data: Optional[Dict] = None
    error_message: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "operation_type": self.operation_type.value,
            "command": self.command,
            "parameters": self.parameters,
            "status": self.status.value,
            "request_payload": self.request_payload,
            "response_data": self.response_data,
            "error_message": self.error_message,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
            "metadata": self.metadata
        }


# ============= 操作日志管理器 =============
class OperationLogger:
    """操作日志管理器"""
    
    def __init__(self, log_file: str = "tool_operations.jsonl"):
        self.log_file = log_file
        self.operations: List[OperationRecord] = []
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ToolOperations")
    
    def log_operation(self, record: OperationRecord):
        """记录操作"""
        self.operations.append(record)
        
        # 写入文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + '\n')
        
        # 打印日志
        self.logger.info(
            f"[{record.tool_name}] {record.operation_type.value} - "
            f"{record.command} - {record.status.value}"
        )
    
    def get_operations_by_tool(self, tool_name: str) -> List[OperationRecord]:
        """获取特定工具的操作记录"""
        return [op for op in self.operations if op.tool_name == tool_name]
    
    def get_failed_operations(self) -> List[OperationRecord]:
        """获取失败的操作"""
        return [op for op in self.operations if op.status == OperationStatus.FAILED]
    
    def get_operation_stats(self) -> Dict[str, Any]:
        """获取操作统计"""
        total = len(self.operations)
        success = len([op for op in self.operations if op.status == OperationStatus.SUCCESS])
        failed = len([op for op in self.operations if op.status == OperationStatus.FAILED])
        
        avg_duration = 0
        if self.operations:
            durations = [op.duration_ms for op in self.operations if op.duration_ms]
            avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_operations": total,
            "success_count": success,
            "failed_count": failed,
            "success_rate": success / total if total > 0 else 0,
            "avg_duration_ms": avg_duration,
            "tools_used": list(set([op.tool_name for op in self.operations]))
        }


# ============= 工具操作执行器 =============
class ToolOperationsSpecialist:
    """工具操作专家 Agent"""
    
    def __init__(self, max_retries: int = 3):
        self.role = ToolOperationsRole()
        self.logger = OperationLogger()
        self.max_retries = max_retries
        
        # 工具配置
        self.tool_configs = {
            "langfuse": {
                "base_url": os.getenv("LANGFUSE_API_URL", "http://localhost:3000"),
                "api_key": os.getenv("LANGFUSE_API_KEY", ""),
                "secret_key": os.getenv("LANGFUSE_SECRET_KEY", "")
            },
            "github": {
                "base_url": "https://api.github.com",
                "token": os.getenv("GITHUB_TOKEN", "")
            }
        }
    
    def execute_operation(
        self,
        tool_name: str,
        operation_type: OperationType,
        command: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> OperationRecord:
        """执行工具操作"""
        
        # 生成操作 ID
        operation_id = f"{tool_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # 创建操作记录
        record = OperationRecord(
            operation_id=operation_id,
            tool_name=tool_name,
            operation_type=operation_type,
            command=command,
            parameters=parameters,
            status=OperationStatus.PENDING
        )
        
        # 记录开始时间
        record.start_time = datetime.now()
        record.status = OperationStatus.IN_PROGRESS
        
        try:
            # 执行具体操作
            if tool_name == "langfuse":
                result = self._execute_langfuse_operation(command, parameters)
            elif tool_name == "github":
                result = self._execute_github_operation(command, parameters)
            else:
                raise ValueError(f"Unsupported tool: {tool_name}")
            
            # 记录成功
            record.status = OperationStatus.SUCCESS
            record.response_data = result
            record.end_time = datetime.now()
            record.duration_ms = (record.end_time - record.start_time).total_seconds() * 1000
            
        except Exception as e:
            # 记录失败
            record.status = OperationStatus.FAILED
            record.error_message = str(e)
            record.end_time = datetime.now()
            record.duration_ms = (record.end_time - record.start_time).total_seconds() * 1000
            
            # 尝试重试
            if record.retry_count < self.max_retries:
                record.retry_count += 1
                record.status = OperationStatus.RETRYING
                self.logger.log_operation(record)
                return self.execute_operation(tool_name, operation_type, command, parameters, **kwargs)
        
        # 记录操作
        self.logger.log_operation(record)
        
        return record
    
    def _execute_langfuse_operation(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Langfuse 操作"""
        config = self.tool_configs["langfuse"]
        
        if command == "get_projects":
            response = requests.get(
                f"{config['base_url']}/api/projects",
                auth=(config['api_key'], config['secret_key']),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        elif command == "get_project_stats":
            project_id = parameters.get("project_id")
            response = requests.get(
                f"{config['base_url']}/api/projects/{project_id}/stats",
                auth=(config['api_key'], config['secret_key']),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        elif command == "get_traces":
            project_id = parameters.get("project_id")
            limit = parameters.get("limit", 10)
            response = requests.get(
                f"{config['base_url']}/api/projects/{project_id}/traces",
                params={"limit": limit},
                auth=(config['api_key'], config['secret_key']),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        else:
            raise ValueError(f"Unknown Langfuse command: {command}")
    
    def _execute_github_operation(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行 GitHub 操作"""
        config = self.tool_configs["github"]
        headers = {"Authorization": f"token {config['token']}"}
        
        if command == "get_repos":
            response = requests.get(
                f"{config['base_url']}/user/repos",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        elif command == "get_repo":
            owner = parameters.get("owner")
            repo = parameters.get("repo")
            response = requests.get(
                f"{config['base_url']}/repos/{owner}/{repo}",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        else:
            raise ValueError(f"Unknown GitHub command: {command}")
    
    def get_operation_history(
        self,
        tool_name: Optional[str] = None,
        status: Optional[OperationStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取操作历史"""
        operations = self.logger.operations
        
        if tool_name:
            operations = [op for op in operations if op.tool_name == tool_name]
        
        if status:
            operations = [op for op in operations if op.status == status]
        
        return [op.to_dict() for op in operations[-limit:]]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.logger.get_operation_stats()
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Agent 信息"""
        return {
            "role": self.role.TITLE,
            "role_cn": self.role.TITLE_CN,
            "responsibilities": self.role.RESPONSIBILITIES,
            "skills": self.role.SKILLS,
            "supported_tools": self.role.SUPPORTED_TOOLS
        }


# ============= 测试 =============
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 工具操作专家 Agent")
    print("="*60)
    
    agent = ToolOperationsSpecialist()
    info = agent.get_info()
    
    print(f"\n📋 职位: {info['role_cn']} ({info['role']})")
    print(f"\n🎯 职责:")
    for r in info['responsibilities']:
        print(f"  • {r}")
    
    print(f"\n💪 技能:")
    for s in info['skills']:
        print(f"  • {s}")
    
    print(f"\n🛠️  支持的工具:")
    for t in info['supported_tools']:
        print(f"  • {t}")
    
    print("\n" + "="*60)
    print("📝 示例操作（不实际执行，仅展示）")
    print("="*60)
    
    print("\n示例 1: 查询 Langfuse 项目")
    print("  agent.execute_operation(")
    print("      tool_name='langfuse',")
    print("      operation_type=OperationType.QUERY,")
    print("      command='get_projects',")
    print("      parameters={}")
    print("  )")
    
    print("\n示例 2: 获取项目统计")
    print("  agent.execute_operation(")
    print("      tool_name='langfuse',")
    print("      operation_type=OperationType.READ,")
    print("      command='get_project_stats',")
    print("      parameters={'project_id': 'xxx'}")
    print("  )")
    
    print("\n" + "="*60)
    print("✅ 所有操作都会被自动记录到 tool_operations.jsonl")
    print("="*60 + "\n")

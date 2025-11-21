"""
Monitoring & Analytics Specialist Agent
监控与分析专家 Agent - 负责系统监控、性能分析、数据追踪
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from pydantic import BaseModel


# ============= Agent 职能定义 =============
class SpecialistRole:
    """监控与分析专家的职能"""
    
    TITLE = "Monitoring & Analytics Specialist"
    TITLE_CN = "监控与分析专家"
    
    RESPONSIBILITIES = [
        "系统性能监控",
        "数据追踪与分析",
        "错误诊断与报告",
        "健康检查",
        "生成分析报告"
    ]
    
    SKILLS = [
        "performance_monitoring",   # 性能监控
        "data_analytics",           # 数据分析
        "error_diagnosis",          # 错误诊断
        "reporting",                # 报告生成
        "system_health_check",      # 健康检查
        "trace_analysis"            # 追踪分析
    ]
    
    TOOLS = [
        "langfuse",     # 使用 Langfuse 作为监控工具
        "prometheus",   # 可扩展到 Prometheus
        "grafana",      # 可扩展到 Grafana
        "elk"           # 可扩展到 ELK Stack
    ]


# ============= 配置 =============
MONITORING_BACKEND = os.getenv("MONITORING_BACKEND", "langfuse")
LANGFUSE_API_URL = os.getenv("LANGFUSE_API_URL", "http://localhost:3000")
LANGFUSE_API_KEY = os.getenv("LANGFUSE_API_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")


# ============= 数据模型 =============
class AnalysisTask(Enum):
    """分析任务类型"""
    DAILY_REPORT = "daily_report"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TRACE_ANALYSIS = "trace_analysis"
    HEALTH_CHECK = "health_check"
    CUSTOM_QUERY = "custom_query"


@dataclass
class MonitoringMetrics:
    """监控指标"""
    total_requests: int = 0
    success_rate: float = 0.0
    avg_latency: float = 0.0
    error_rate: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    last_24h_requests: int = 0
    last_24h_errors: int = 0


class AgentState(BaseModel):
    """Agent 状态"""
    task_id: str
    task_type: AnalysisTask
    project_id: Optional[str] = None
    time_range: str = "24h"
    action: str = ""
    metrics: Optional[MonitoringMetrics] = None
    result: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    messages: List[BaseMessage] = field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


# ============= 监控工具（通用接口）=============
@tool
def get_system_list() -> Dict[str, Any]:
    """获取所有被监控的系统/项目列表"""
    try:
        if MONITORING_BACKEND == "langfuse":
            response = requests.get(
                f"{LANGFUSE_API_URL}/api/projects",
                auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
                timeout=10
            )
            response.raise_for_status()
            return {
                "status": "success",
                "systems": response.json().get("data", [])
            }
        else:
            return {"status": "error", "error": "Unsupported backend"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@tool
def get_performance_metrics(system_id: str, time_range: str = "24h") -> Dict[str, Any]:
    """获取系统性能指标"""
    try:
        if MONITORING_BACKEND == "langfuse":
            response = requests.get(
                f"{LANGFUSE_API_URL}/api/projects/{system_id}/stats",
                auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
                timeout=10
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            
            return {
                "status": "success",
                "system_id": system_id,
                "metrics": {
                    "total_requests": data.get("total_traces", 0),
                    "success_rate": data.get("success_rate", 0.0),
                    "avg_latency": data.get("avg_latency_ms", 0.0),
                    "error_rate": data.get("error_rate", 0.0),
                    "p95_latency": data.get("p95_latency_ms", 0.0),
                    "p99_latency": data.get("p99_latency_ms", 0.0)
                }
            }
        else:
            return {"status": "error", "error": "Unsupported backend"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@tool
def get_error_logs(system_id: str, limit: int = 20) -> Dict[str, Any]:
    """获取错误日志"""
    try:
        if MONITORING_BACKEND == "langfuse":
            response = requests.get(
                f"{LANGFUSE_API_URL}/api/projects/{system_id}/traces",
                params={"status": "error", "limit": limit},
                auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
                timeout=10
            )
            response.raise_for_status()
            return {
                "status": "success",
                "errors": response.json().get("data", [])
            }
        else:
            return {"status": "error", "error": "Unsupported backend"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@tool
def get_trace_details(system_id: str, trace_id: str) -> Dict[str, Any]:
    """获取追踪详情"""
    try:
        if MONITORING_BACKEND == "langfuse":
            response = requests.get(
                f"{LANGFUSE_API_URL}/api/projects/{system_id}/traces/{trace_id}",
                auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
                timeout=10
            )
            response.raise_for_status()
            return {
                "status": "success",
                "trace": response.json().get("data", {})
            }
        else:
            return {"status": "error", "error": "Unsupported backend"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@tool
def generate_health_report(system_id: str) -> Dict[str, Any]:
    """生成系统健康报告"""
    try:
        # 获取性能指标
        metrics = get_performance_metrics(system_id, "24h")
        
        if metrics.get("status") != "success":
            return metrics
        
        m = metrics["metrics"]
        
        # 健康评分（0-100）
        health_score = 100
        issues = []
        
        # 检查错误率
        if m["error_rate"] > 0.05:  # 超过 5%
            health_score -= 30
            issues.append(f"错误率过高: {m['error_rate']*100:.1f}%")
        elif m["error_rate"] > 0.01:  # 超过 1%
            health_score -= 10
            issues.append(f"错误率偏高: {m['error_rate']*100:.1f}%")
        
        # 检查延迟
        if m["avg_latency"] > 5000:  # 超过 5s
            health_score -= 20
            issues.append(f"平均延迟过高: {m['avg_latency']:.0f}ms")
        elif m["avg_latency"] > 2000:  # 超过 2s
            health_score -= 10
            issues.append(f"平均延迟偏高: {m['avg_latency']:.0f}ms")
        
        # 检查成功率
        if m["success_rate"] < 0.95:  # 低于 95%
            health_score -= 20
            issues.append(f"成功率偏低: {m['success_rate']*100:.1f}%")
        
        # 健康等级
        if health_score >= 90:
            health_status = "优秀"
        elif health_score >= 70:
            health_status = "良好"
        elif health_score >= 50:
            health_status = "一般"
        else:
            health_status = "需要关注"
        
        return {
            "status": "success",
            "system_id": system_id,
            "health_score": health_score,
            "health_status": health_status,
            "metrics": m,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============= Agent 执行逻辑 =============
class MonitoringSpecialistAgent:
    """监控与分析专家 Agent"""
    
    def __init__(self):
        self.role = SpecialistRole()
        self.tools = [
            get_system_list,
            get_performance_metrics,
            get_error_logs,
            get_trace_details,
            generate_health_report
        ]
    
    def execute_task(self, task_type: AnalysisTask, system_id: Optional[str] = None) -> Dict[str, Any]:
        """执行分析任务"""
        
        if task_type == AnalysisTask.HEALTH_CHECK:
            if not system_id:
                systems = get_system_list()
                if systems["status"] == "success" and systems["systems"]:
                    system_id = systems["systems"][0]["id"]
                else:
                    return {"status": "error", "error": "No system found"}
            
            return generate_health_report(system_id)
        
        elif task_type == AnalysisTask.PERFORMANCE_ANALYSIS:
            return get_performance_metrics(system_id or "default", "24h")
        
        elif task_type == AnalysisTask.ERROR_ANALYSIS:
            return get_error_logs(system_id or "default", 20)
        
        else:
            return {"status": "error", "error": "Unsupported task type"}
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Agent 信息"""
        return {
            "role": self.role.TITLE,
            "role_cn": self.role.TITLE_CN,
            "responsibilities": self.role.RESPONSIBILITIES,
            "skills": self.role.SKILLS,
            "available_tools": [t for t in self.role.TOOLS]
        }

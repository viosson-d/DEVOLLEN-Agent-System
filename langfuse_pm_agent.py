import os
import json
import requests
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from pydantic import BaseModel

# ============= Configuration =============
LANGFUSE_API_URL = os.getenv("LANGFUSE_API_URL", "http://localhost:3000")
LANGFUSE_API_KEY = os.getenv("LANGFUSE_API_KEY", "demo-pk-123456")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "demo-sk-123456")

# ============= Data Models =============
class TaskType(Enum):
    DAILY_REPORT = "daily_report"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TRACE_ANALYSIS = "trace_analysis"
    HEALTH_CHECK = "health_check"

@dataclass
class AgentState(BaseModel):
    task_id: str
    task_type: TaskType
    project_id: Optional[str] = None
    action: str = ""
    result: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    messages: List[BaseMessage] = field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True

# ============= Langfuse API Tools =============
@tool
def get_projects() -> Dict[str, Any]:
    try:
        response = requests.get(
            f"{LANGFUSE_API_URL}/api/projects",
            auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
            timeout=10
        )
        response.raise_for_status()
        return {"status": "success", "projects": response.json().get("data", [])}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@tool
def get_project_stats(project_id: str) -> Dict[str, Any]:
    try:
        response = requests.get(
            f"{LANGFUSE_API_URL}/api/projects/{project_id}/stats",
            auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
            timeout=10
        )
        response.raise_for_status()
        return {"status": "success", "stats": response.json().get("data", {})}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@tool
def get_recent_traces(project_id: str, limit: int = 10) -> Dict[str, Any]:
    try:
        response = requests.get(
            f"{LANGFUSE_API_URL}/api/projects/{project_id}/traces",
            params={"limit": limit},
            auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
            timeout=10
        )
        response.raise_for_status()
        return {"status": "success", "traces": response.json().get("data", [])}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@tool
def get_recent_errors(project_id: str, hours: int = 24) -> Dict[str, Any]:
    try:
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        response = requests.get(
            f"{LANGFUSE_API_URL}/api/projects/{project_id}/errors",
            params={"since": since},
            auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
            timeout=10
        )
        response.raise_for_status()
        return {"status": "success", "errors": response.json().get("data", [])}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@tool
def check_project_health(project_id: str) -> Dict[str, Any]:
    try:
        stats_response = requests.get(
            f"{LANGFUSE_API_URL}/api/projects/{project_id}/stats",
            auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
            timeout=10
        )
        stats_response.raise_for_status()
        stats = stats_response.json().get("data", {})
        
        errors_response = requests.get(
            f"{LANGFUSE_API_URL}/api/projects/{project_id}/errors",
            auth=(LANGFUSE_API_KEY, LANGFUSE_SECRET_KEY),
            timeout=10
        )
        errors = errors_response.json().get("data", []) if errors_response.ok else []
        
        health_status = "healthy"
        alerts = []
        
        if len(errors) > 10:
            health_status = "warning"
            alerts.append(f"Latest {len(errors)} errors detected")
        
        return {
            "status": "success",
            "health": {
                "status": health_status,
                "alerts": alerts,
                "stats": stats,
                "error_count": len(errors)
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============= Workflow Nodes =============
def analyze_task_node(state: Dict[str, Any]) -> Dict[str, Any]:
    task_type = state.get("task_type")
    project_id = state.get("project_id")
    
    print(f"\nAnalyzing: {task_type}")
    state["status"] = "analyzing"
    state["action"] = f"Analyzing {task_type} task"
    
    if not project_id:
        try:
            projects_result = get_projects.invoke({})
            if projects_result.get("status") == "success":
                projects = projects_result.get("projects", [])
                if projects:
                    state["project_id"] = projects[0].get("id")
        except Exception as e:
            state["project_id"] = "demo-project"
    
    return state

def execute_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    task_type = state.get("task_type")
    project_id = state.get("project_id") or "demo-project"
    
    state["status"] = "executing"
    
    if task_type == TaskType.DAILY_REPORT.value:
        result = {}
        try:
            health = check_project_health.invoke({"project_id": project_id})
            result["health"] = health.get("health", {})
        except Exception as e:
            result["health"] = {"status": "unknown", "error": str(e)}
        
        try:
            stats = get_project_stats.invoke({"project_id": project_id})
            result["stats"] = stats.get("stats", {})
        except Exception as e:
            result["stats"] = {}
        
        try:
            traces = get_recent_traces.invoke({"project_id": project_id, "limit": 5})
            result["recent_traces"] = traces.get("traces", [])
        except Exception as e:
            result["recent_traces"] = []
        
        try:
            errors = get_recent_errors.invoke({"project_id": project_id, "hours": 24})
            result["recent_errors"] = errors.get("errors", [])
        except Exception as e:
            result["recent_errors"] = []
        
        state["result"] = result
        state["action"] = "Daily report generated"
    
    elif task_type == TaskType.ERROR_ANALYSIS.value:
        try:
            errors = get_recent_errors.invoke({"project_id": project_id, "hours": 24})
            state["result"] = {"errors": errors.get("errors", []), "error_count": len(errors.get("errors", []))}
        except Exception as e:
            state["result"] = {"errors": [], "error_count": 0, "error": str(e)}
        state["action"] = "Error analysis completed"
    
    elif task_type == TaskType.PERFORMANCE_ANALYSIS.value:
        try:
            stats = get_project_stats.invoke({"project_id": project_id})
            state["result"] = stats.get("stats", {})
        except Exception as e:
            state["result"] = {"error": str(e)}
        state["action"] = "Performance analysis completed"
    
    elif task_type == TaskType.HEALTH_CHECK.value:
        try:
            health = check_project_health.invoke({"project_id": project_id})
            state["result"] = health.get("health", {})
        except Exception as e:
            state["result"] = {"status": "error", "error": str(e)}
        state["action"] = "Health check completed"
    
    return state

def generate_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["status"] = "completed"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "task_id": state.get("task_id"),
        "task_type": state.get("task_type"),
        "project_id": state.get("project_id"),
        "action": state.get("action"),
        "result": state.get("result"),
        "status": state.get("status")
    }
    
    message = AIMessage(content=json.dumps(report, indent=2, ensure_ascii=False))
    state["messages"].append(message)
    
    return state

# ============= Build Workflow =============
def build_workflow():
    workflow = StateGraph(dict)
    workflow.add_node("analyze", analyze_task_node)
    workflow.add_node("execute", execute_action_node)
    workflow.add_node("report", generate_report_node)
    workflow.add_edge("analyze", "execute")
    workflow.add_edge("execute", "report")
    workflow.add_edge("report", END)
    workflow.set_entry_point("analyze")
    return workflow.compile()

# ============= Main Agent Class =============
class LangfuseProjectManagerAgent:
    def __init__(self):
        self.graph = build_workflow()
        self.id = "langfuse_pm_001"
        self.name = "Langfuse Project Manager"
    
    def execute_task(self, task_type: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        task_id = f"task_{datetime.now().timestamp()}"
        state = {
            "task_id": task_id,
            "task_type": task_type,
            "project_id": project_id,
            "action": "",
            "result": {},
            "status": "pending",
            "messages": [HumanMessage(content=f"Execute: {task_type}")]
        }
        
        try:
            result = self.graph.invoke(state)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e), "task_id": task_id}
    
    def generate_daily_report(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        return self.execute_task(TaskType.DAILY_REPORT.value, project_id)
    
    def analyze_errors(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        return self.execute_task(TaskType.ERROR_ANALYSIS.value, project_id)
    
    def analyze_performance(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        return self.execute_task(TaskType.PERFORMANCE_ANALYSIS.value, project_id)
    
    def check_health(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        return self.execute_task(TaskType.HEALTH_CHECK.value, project_id)

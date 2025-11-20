"""
DEVOLLEN Agent Library - Agent Employees
Agent 员工库 - 用于管理各种自动化任务的 AI Agent
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum


class AgentRole(Enum):
    """Agent 角色定义"""
    PROJECT_MANAGER = "project_manager"  # 项目经理
    DATA_ANALYST = "data_analyst"  # 数据分析员
    DEVELOPER = "developer"  # 开发员
    REVIEWER = "reviewer"  # 审核员
    MANAGER = "manager"  # 经理


@dataclass
class Agent:
    """Agent 基础类"""
    id: str
    name: str
    role: AgentRole
    description: str
    instructions: str
    tools: list = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []


class AgentEmployeeLibrary:
    """Agent 员工库 - 管理所有 Agent"""
    
    def __init__(self):
        self.agents: dict = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """注册默认 Agent"""
        pass
    
    def register_agent(self, agent: Agent):
        """注册新 Agent"""
        self.agents[agent.id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取 Agent"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> list:
        """列出所有 Agent"""
        return list(self.agents.values())


# 全局 Agent 库实例
agent_library = AgentEmployeeLibrary()

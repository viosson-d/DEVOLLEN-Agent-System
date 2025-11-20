import json
from typing import Any, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class AgentRole(Enum):
    """Agent 角色"""
    LANGFUSE_PM = "langfuse_project_manager"  # Langfuse 项目经理
    DATA_ANALYST = "data_analyst"  # 数据分析员
    DEVELOPER = "developer"  # 开发员
    REVIEWER = "code_reviewer"  # 代码审核员
    MANAGER = "team_manager"  # 团队经理


class AgentStatus(Enum):
    """Agent 状态"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentProfile:
    """Agent 配置文件"""
    id: str
    name: str
    role: AgentRole
    description: str
    instructions: str
    tools: List[str]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class AgentTask:
    """Agent 任务"""
    id: str
    agent_id: str
    task: str
    status: AgentStatus = AgentStatus.IDLE
    result: Any = None
    created_at: str = None
    completed_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class AgentEmployeeSystem:
    """Agent 员工系统 - 管理所有 Agent 和任务"""
    
    def __init__(self, storage_file: str = "/Users/viosson/agents_config.json"):
        self.storage_file = storage_file
        self.agents: Dict[str, AgentProfile] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.load_agents()
    
    def register_agent(self, profile: AgentProfile) -> bool:
        """注册新 Agent"""
        if profile.id in self.agents:
            print(f"⚠️ Agent {profile.id} 已存在")
            return False
        
        self.agents[profile.id] = profile
        self.save_agents()
        print(f"✓ Agent '{profile.name}' 注册成功")
        return True
    
    def get_agent(self, agent_id: str) -> AgentProfile:
        """获取 Agent"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[AgentProfile]:
        """列出所有 Agent"""
        return list(self.agents.values())
    
    def create_task(self, agent_id: str, task: str) -> AgentTask:
        """创建任务"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} 不存在")
        
        task_id = f"task_{len(self.tasks)}_{datetime.now().timestamp()}"
        agent_task = AgentTask(
            id=task_id,
            agent_id=agent_id,
            task=task
        )
        self.tasks[task_id] = agent_task
        return agent_task
    
    def get_task(self, task_id: str) -> AgentTask:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: AgentStatus, result: Any = None):
        """更新任务状态"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            task.result = result
            if status == AgentStatus.COMPLETED:
                task.completed_at = datetime.now().isoformat()
    
    def save_agents(self):
        """保存 Agent 配置"""
        agents_data = []
        for agent in self.agents.values():
            agent_dict = asdict(agent)
            # 转换 Enum 为字符串
            agent_dict['role'] = agent_dict['role'].value
            agents_data.append(agent_dict)
        
        data = {
            "agents": agents_data,
            "saved_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_agents(self):
        """加载 Agent 配置"""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                for agent_data in data.get("agents", []):
                    role_str = agent_data["role"]
                    try:
                        role = AgentRole(role_str)
                    except (ValueError, KeyError):
                        role = AgentRole.LANGFUSE_PM
                    
                    profile = AgentProfile(
                        id=agent_data["id"],
                        name=agent_data["name"],
                        role=role,
                        description=agent_data["description"],
                        instructions=agent_data["instructions"],
                        tools=agent_data["tools"],
                        created_at=agent_data.get("created_at")
                    )
                    self.agents[profile.id] = profile
        except FileNotFoundError:
            print(f"配置文件不存在: {self.storage_file}")
    
    def print_agent_info(self, agent_id: str):
        """打印 Agent 信息"""
        agent = self.get_agent(agent_id)
        if not agent:
            print(f"❌ Agent {agent_id} 不存在")
            return
        
        print(f"\n{'='*60}")
        print(f"🤖 Agent 信息")
        print(f"{'='*60}")
        print(f"ID:          {agent.id}")
        print(f"名称:        {agent.name}")
        print(f"角色:        {agent.role.value}")
        print(f"描述:        {agent.description}")
        print(f"可用工具:    {', '.join(agent.tools)}")
        print(f"创建时间:    {agent.created_at}")
        print(f"\n📋 系统指令:")
        print(f"{agent.instructions}")
        print(f"{'='*60}\n")


# 创建全局系统实例
agent_system = AgentEmployeeSystem()


def setup_default_agents():
    """设置默认 Agent"""
    
    # Langfuse 项目负责人
    langfuse_pm = AgentProfile(
        id="langfuse_pm_001",
        name="Langfuse 项目负责人",
        role=AgentRole.LANGFUSE_PM,
        description="负责管理和监控 Langfuse 项目，生成报告，分析错误和性能",
        instructions="""你是 DEVOLLEN 系统的 Langfuse 项目负责人。
你的职责包括：
1. 监控项目的 Trace 数据和会话
2. 分析项目的性能指标和错误率
3. 生成日报和周报
4. 识别性能瓶颈并提出优化建议
5. 管理项目的 API Key 和权限

你应该：
- 主动监控项目健康状态
- 及时报告异常情况
- 提供数据驱动的建议
- 保持详细的变更日志""",
        tools=[
            "get_project_list",
            "get_project_stats",
            "get_recent_errors",
            "get_traces",
            "generate_daily_report",
            "get_performance_metrics"
        ]
    )
    
    agent_system.register_agent(langfuse_pm)
    
    # 数据分析员
    data_analyst = AgentProfile(
        id="data_analyst_001",
        name="数据分析员",
        role=AgentRole.DATA_ANALYST,
        description="分析 Langfuse 数据，提供洞察和建议",
        instructions="""你是数据分析员，负责深度分析 Langfuse 项目数据。
你的职责包括：
1. 分析用户行为和模式
2. 识别性能趋势
3. 发现异常和问题
4. 生成分析报告和可视化
5. 提供数据驱动的建议

你应该使用统计学和数据科学方法。""",
        tools=[
            "query_traces",
            "analyze_performance",
            "generate_insights",
            "create_dashboards"
        ]
    )
    
    agent_system.register_agent(data_analyst)
    
    # 开发员
    developer = AgentProfile(
        id="developer_001",
        name="开发员",
        role=AgentRole.DEVELOPER,
        description="处理开发任务和代码实现",
        instructions="""你是开发员，负责代码实现和功能开发。
你应该：
- 编写高质量的代码
- 遵循最佳实践
- 进行充分的测试
- 提供清晰的文档""",
        tools=[
            "write_code",
            "run_tests",
            "debug",
            "generate_documentation"
        ]
    )
    
    agent_system.register_agent(developer)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 DEVOLLEN Agent 员工库系统")
    print("="*60)
    
    setup_default_agents()
    
    print(f"\n📚 已注册的 Agent:\n")
    for agent in agent_system.list_agents():
        print(f"✓ {agent.name}")
        print(f"  ID: {agent.id}")
        print(f"  工具: {len(agent.tools)} 个\n")

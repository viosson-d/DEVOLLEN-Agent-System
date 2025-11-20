# 🤖 DEVOLLEN Agent 员工库系统

完整的 AI Agent 框架，用于自动化任务管理、工作流协调和智能决策。

## 📋 目录结构

```
DEVOLLEN Agent System
├── agent_system.py           # Agent 员工库系统核心
├── agent_library.py          # Agent 基类和角色定义  
├── langfuse_pm_agent.py      # Langfuse Project Manager Agent
├── agent_orchestrator.py     # Agent 协调器
├── devollen_agent.py         # CLI 管理工具
├── quickstart.py             # 快速启动指南
└── agent_demo.py             # 完整演示脚本
```

## 🎯 核心概念

### Agent 角色 (AgentRole)

系统预定义了以下 Agent 角色：

| 角色 | ID | 描述 | 职责 |
|------|-----|------|------|
| **Langfuse 项目经理** | `langfuse_pm_001` | 项目监控和报告 | 监控 Trace、生成报告、错误分析 |
| **数据分析员** | `data_analyst_001` | 数据深度分析 | 性能分析、趋势识别、洞察生成 |
| **开发员** | `developer_001` | 代码实现 | 编码、测试、文档 |
| **代码审核员** | `reviewer_001` | 代码质量 | 代码审查、最佳实践检查 |
| **团队经理** | `manager_001` | 团队协调 | 任务分配、进度跟踪、报告汇总 |

### 任务优先级 (TaskPriority)

```
LOW       (1)  - 低优先级任务
NORMAL    (2)  - 普通优先级（默认）
HIGH      (3)  - 高优先级任务
URGENT    (4)  - 紧急任务
```

### 任务状态 (TaskStatus)

```
PENDING   - 待执行
ASSIGNED  - 已分配
EXECUTING - 执行中
COMPLETED - 已完成
FAILED    - 执行失败
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install langgraph langchain pydantic requests
```

### 2. 初始化系统

```python
from agent_system import AgentEmployeeSystem, setup_default_agents

system = AgentEmployeeSystem()
setup_default_agents()
```

### 3. 创建和管理任务

```python
# 创建任务
task = system.create_task("langfuse_pm_001", "执行监控")

# 更新任务状态
from agent_system import AgentStatus
system.update_task_status(task.id, AgentStatus.COMPLETED)
```

## 📚 模块说明

### agent_system.py

Agent 员工库系统核心，管理所有 Agent 的配置、注册和持久化。

**主要类**:
- `AgentRole`: Agent 角色枚举
- `AgentStatus`: Agent 状态枚举
- `AgentProfile`: Agent 配置文件
- `AgentTask`: Agent 任务
- `AgentEmployeeSystem`: 主系统类

**主要方法**:
```python
system.register_agent(profile)      # 注册新 Agent
system.list_agents()                # 列出所有 Agent
system.create_task(agent_id, task)  # 创建任务
system.update_task_status(...)      # 更新任务状态
system.save_agents()                # 保存配置
system.load_agents()                # 加载配置
```

### agent_orchestrator.py

协调多个 Agent 的协作和工作流执行。

**主要类**:
- `TaskPriority`: 任务优先级枚举
- `TaskStatus`: 任务状态枚举
- `Task`: 任务定义
- `AgentOrchestrator`: 协调器主类

**主要方法**:
```python
orchestrator.register_agent(id, agent)           # 注册 Agent
orchestrator.create_task(...)                    # 创建任务
orchestrator.execute_task(task_id)              # 执行任务
orchestrator.execute_workflow(tasks)            # 执行工作流
orchestrator.create_daily_pipeline(...)         # 创建日常工作流
orchestrator.get_statistics()                   # 获取统计信息
```

### langfuse_pm_agent.py

Langfuse 项目管理 Agent，使用 Langgraph 实现状态机工作流。

**主要类**:
- `TaskType`: 任务类型枚举
- `AgentState`: Agent 状态
- `LangfuseProjectManagerAgent`: 主 Agent 类

**主要方法**:
```python
agent.generate_daily_report(project_id)    # 生成日报
agent.analyze_errors(project_id)           # 分析错误
agent.analyze_performance(project_id)      # 分析性能
agent.check_health(project_id)             # 检查健康状态
```

## 🔧 实际使用示例

### 示例 1: 基础 Agent 系统

```python
from agent_system import AgentEmployeeSystem, setup_default_agents

# 创建系统
system = AgentEmployeeSystem()
setup_default_agents()

# 列出 Agent
for agent in system.list_agents():
    print(f"{agent.name}: {agent.description}")

# 创建任务
task = system.create_task("langfuse_pm_001", "执行日常监控")
```

### 示例 2: 使用协调器

```python
from agent_orchestrator import AgentOrchestrator, TaskPriority
from langfuse_pm_agent import LangfuseProjectManagerAgent

# 初始化
orchestrator = AgentOrchestrator()
agent = LangfuseProjectManagerAgent()

# 注册 Agent
orchestrator.register_agent("langfuse_pm_001", agent)

# 创建任务
task = orchestrator.create_task(
    agent_id="langfuse_pm_001",
    name="项目监控",
    description="监控 Langfuse 项目",
    parameters={"type": "health_check", "project_id": "demo"},
    priority=TaskPriority.HIGH
)

# 执行任务
result = orchestrator.execute_task(task.id)
```

### 示例 3: 日常工作流

```python
# 创建日常工作流
task_ids = orchestrator.create_daily_pipeline(project_id="demo")

# 执行工作流
tasks = [orchestrator.tasks[tid] for tid in task_ids]
results = orchestrator.execute_workflow(tasks)

# 查看统计
stats = orchestrator.get_statistics()
print(f"成功率: {stats['success_rate']}")
```

## 🌐 环境配置

### 环境变量

```bash
export LANGFUSE_API_URL="http://localhost:3000"
export LANGFUSE_API_KEY="your-api-key"
export LANGFUSE_SECRET_KEY="your-secret-key"
```

### 配置文件

Agent 配置保存在 `agents_config.json`:

```json
{
  "agents": [
    {
      "id": "langfuse_pm_001",
      "name": "Langfuse 项目经理",
      "role": "langfuse_project_manager",
      "description": "...",
      "instructions": "...",
      "tools": ["tool1", "tool2"],
      "created_at": "2025-11-21T10:00:00"
    }
  ]
}
```

## 📊 工作流示例

### 晨间工作流

```
晨间检查
├── 1. 项目健康检查
├── 2. 获取 24 小时统计数据
├── 3. 检查告警
└── 4. 生成晨间报告
```

### 日报工作流

```
日报生成
├── 1. 收集 Trace 数据
├── 2. 分析错误
├── 3. 计算性能指标
└── 4. 生成日报文档
```

## 🎓 架构图

```
┌──────────────────────────────────────────────────────┐
│           DEVOLLEN Agent System                      │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │   Agent Employee System (员工库)          │    │
│  │   - 角色定义                              │    │
│  │   - Agent 注册                            │    │
│  │   - 配置管理                              │    │
│  └────────────────────────────────────────────┘    │
│                       │                             │
│                       ▼                             │
│  ┌────────────────────────────────────────────┐    │
│  │   Agent Orchestrator (协调器)             │    │
│  │   - 任务创建                              │    │
│  │   - 工作流管理                            │    │
│  │   - 执行监控                              │    │
│  └────────────────────────────────────────────┘    │
│                       │                             │
│         ┌─────────────┼─────────────┐              │
│         ▼             ▼             ▼              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │   Agent    │ │   Agent    │ │   Agent    │   │
│  │            │ │            │ │            │   │
│  │ • Tools    │ │ • Tools    │ │ • Tools    │   │
│  │ • Tasks    │ │ • Tasks    │ │ • Tasks    │   │
│  │ • Results  │ │ • Results  │ │ • Results  │   │
│  └────────────┘ └────────────┘ └────────────┘   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## 🐛 故障排除

### 导入错误

确保所有文件都在同一目录或 Python 路径中：

```python
import sys
sys.path.insert(0, '/path/to/agent/system')
```

### API 连接错误

检查 Langfuse 服务和环境变量：

```bash
echo $LANGFUSE_API_URL
echo $LANGFUSE_API_KEY
```

### 任务执行失败

查看错误日志：

```python
task = orchestrator.tasks[task_id]
if task.status.value == "failed":
    print(f"错误: {task.error}")
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**更新时间**: 2025-11-21  
**版本**: 1.0.0  
**作者**: DEVOLLEN Team

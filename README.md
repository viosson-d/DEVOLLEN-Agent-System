# 🤖 DEVOLLEN Agent System

完整的 AI Agent 员工库系统，用于自动化任务管理、工作流协调和智能决策。

## ✨ 核心特性

- **多 Agent 协作**: 支持多个独立的 Agent 并行工作
- **灵活的任务分配**: 基于优先级的智能任务调度
- **完整的生命周期管理**: 创建 → 分配 → 执行 → 报告
- **工作流支持**: 支持复杂的多步骤工作流
- **实时监控**: 任务状态和进度实时跟踪
- **数据持久化**: 保存配置和执行历史
- **Langgraph 集成**: 状态机工作流支持

## 📦 核心模块

### 1. Agent 系统 (`agent_system.py`)
管理所有 Agent 的配置、注册和持久化。

**功能**:
- Agent 注册和管理
- 5 个预定义角色 (PM, 分析员, 开发员, 审核员, 经理)
- 任务创建和跟踪
- 配置文件持久化

### 2. Agent 协调器 (`agent_orchestrator.py`)
协调多个 Agent 的协作和工作流执行。

**功能**:
- 任务创建和分配
- 基于优先级的任务调度
- 工作流管理
- 实时状态监控
- 执行统计和报告

### 3. Langfuse Project Manager Agent (`langfuse_pm_agent.py`)
使用 Langgraph 实现的项目管理 Agent。

**功能**:
- 5 个任务类型 (日报、错误分析、性能分析、Trace 分析、健康检查)
- Langgraph 状态机工作流
- Langfuse API 集成
- 实时数据检索和分析

### 4. CLI 管理工具 (`devollen_agent.py`)
统一的命令行界面用于管理整个系统。

**命令**:
- `init` - 初始化系统
- `list` - 列出所有 Agent
- `health` - 检查项目健康状态
- `errors` - 分析项目错误
- `report` - 生成项目报告
- `pipeline` - 创建日常工作流
- `execute` - 执行所有待执行任务
- `stats` - 显示统计信息

## 🚀 快速开始

### 安装依赖

```bash
pip3 install langgraph langchain pydantic requests
```

### 初始化系统

```bash
python3 devollen_agent.py init
```

### 创建和执行工作流

```python
from agent_system import AgentEmployeeSystem, setup_default_agents
from agent_orchestrator import AgentOrchestrator
from langfuse_pm_agent import LangfuseProjectManagerAgent

# 初始化
system = AgentEmployeeSystem()
setup_default_agents()

orchestrator = AgentOrchestrator()
pm_agent = LangfuseProjectManagerAgent()

# 注册 Agent
orchestrator.register_agent("langfuse_pm_001", pm_agent)

# 创建日常工作流
workflow_tasks = orchestrator.create_daily_pipeline(project_id="my-project")

# 执行工作流
tasks = [orchestrator.tasks[tid] for tid in workflow_tasks]
results = orchestrator.execute_workflow(tasks)
```

## 📚 文档

- **完整 API 文档**: 参考代码中的详细注释
- **快速启动指南**: 运行 `quickstart.py`
- **完整演示**: 运行 `agent_demo.py`

## 🎯 Agent 角色

| 角色 | ID | 描述 |
|------|-----|------|
| **Langfuse 项目经理** | `langfuse_pm_001` | 项目监控和报告 |
| **数据分析员** | `data_analyst_001` | 数据深度分析 |
| **开发员** | `developer_001` | 代码实现 |
| **代码审核员** | `reviewer_001` | 代码质量 |
| **团队经理** | `manager_001` | 团队协调 |

## 📊 任务优先级

- `LOW` (1) - 低优先级任务
- `NORMAL` (2) - 普通优先级（默认）
- `HIGH` (3) - 高优先级任务
- `URGENT` (4) - 紧急任务

## 🔄 任务状态流转

```
PENDING (待执行)
  ↓
ASSIGNED (已分配)
  ↓
EXECUTING (执行中)
  ├→ COMPLETED (已完成)
  └→ FAILED (执行失败)
```

## 🌟 项目亮点

✅ 完整的架构设计  
✅ 模块化的代码结构  
✅ Langgraph 状态机集成  
✅ 完善的文档和示例  
✅ 易于扩展和定制  
✅ 生产级别的质量  

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**版本**: 1.0.0  
**状态**: ✅ 完全就绪  
**最后更新**: 2025-11-21

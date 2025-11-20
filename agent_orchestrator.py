"""
Agent 协调器
管理多个 Agent 的协作和任务分配
"""

import json
from typing import Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    description: str
    agent_id: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str = None
    created_at: str = None
    completed_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class AgentOrchestrator:
    """Agent 协调器"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}  # agent_id -> agent instance
        self.tasks: Dict[str, Task] = {}  # task_id -> task
        self.task_history: List[Task] = []
        self.workflows: Dict[str, List[str]] = {}  # workflow_id -> [task_ids]
    
    def register_agent(self, agent_id: str, agent: Any):
        """注册 Agent"""
        self.agents[agent_id] = agent
        print(f"✓ Agent '{agent_id}' 已注册")
    
    def create_task(
        self,
        agent_id: str,
        name: str,
        description: str,
        parameters: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> Task:
        """创建任务"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} 不存在")
        
        task_id = f"task_{datetime.now().timestamp()}"
        task = Task(
            id=task_id,
            name=name,
            description=description,
            agent_id=agent_id,
            priority=priority,
            parameters=parameters or {}
        )
        
        self.tasks[task_id] = task
        print(f"📋 任务 '{name}' 已创建 (ID: {task_id})")
        return task
    
    def execute_task(self, task_id: str) -> Task:
        """执行单个任务"""
        if task_id not in self.tasks:
            raise ValueError(f"任务 {task_id} 不存在")
        
        task = self.tasks[task_id]
        agent = self.agents.get(task.agent_id)
        
        if not agent:
            task.status = TaskStatus.FAILED
            task.error = f"Agent {task.agent_id} 不存在"
            return task
        
        print(f"\n▶️ 执行任务: {task.name}")
        task.status = TaskStatus.EXECUTING
        
        try:
            if hasattr(agent, 'execute_task'):
                result = agent.execute_task(
                    task.parameters.get('type'),
                    task.parameters.get('project_id')
                )
            else:
                result = {"error": "Agent 不支持 execute_task 方法"}
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            print(f"✓ 任务完成")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            print(f"❌ 任务失败: {str(e)}")
        
        self.task_history.append(task)
        return task
    
    def execute_workflow(self, tasks: List[Task], parallel: bool = False) -> List[Task]:
        """执行工作流（任务序列）"""
        print(f"\n{'='*60}")
        print(f"🔄 执行工作流 ({len(tasks)} 个任务)")
        print(f"{'='*60}")
        
        results = []
        
        if parallel:
            print("⚠️ 并行模式暂未实现，使用顺序执行")
        
        for task in tasks:
            result = self.execute_task(task.id)
            results.append(result)
        
        return results
    
    def create_daily_pipeline(self, project_id: str = None) -> List[str]:
        """创建日常工作流"""
        workflow_name = f"daily_pipeline_{datetime.now().isoformat()}"
        task_ids = []
        
        # 任务 1: 健康检查
        health_task = self.create_task(
            agent_id="langfuse_pm_001",
            name="项目健康检查",
            description="检查 Langfuse 项目的健康状态",
            parameters={"type": "health_check", "project_id": project_id},
            priority=TaskPriority.HIGH
        )
        task_ids.append(health_task.id)
        
        # 任务 2: 错误分析
        error_task = self.create_task(
            agent_id="langfuse_pm_001",
            name="错误分析",
            description="分析过去 24 小时的错误",
            parameters={"type": "error_analysis", "project_id": project_id},
            priority=TaskPriority.NORMAL
        )
        task_ids.append(error_task.id)
        
        # 任务 3: 性能分析
        perf_task = self.create_task(
            agent_id="langfuse_pm_001",
            name="性能分析",
            description="分析项目性能指标",
            parameters={"type": "performance_analysis", "project_id": project_id},
            priority=TaskPriority.NORMAL
        )
        task_ids.append(perf_task.id)
        
        # 任务 4: 生成日报
        report_task = self.create_task(
            agent_id="langfuse_pm_001",
            name="生成日报",
            description="根据分析结果生成日报",
            parameters={"type": "daily_report", "project_id": project_id},
            priority=TaskPriority.HIGH
        )
        task_ids.append(report_task.id)
        
        # 保存工作流
        self.workflows[workflow_name] = task_ids
        
        print(f"\n✓ 日常工作流创建完成 ({len(task_ids)} 个任务)")
        return task_ids
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": f"任务 {task_id} 不存在"}
        
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "progress": self._calculate_progress(task),
            "created_at": task.created_at,
            "completed_at": task.completed_at
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        task_ids = self.workflows.get(workflow_id, [])
        if not task_ids:
            return {"error": f"工作流 {workflow_id} 不存在"}
        
        tasks = [self.tasks.get(tid) for tid in task_ids]
        completed = sum(1 for t in tasks if t and t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in tasks if t and t.status == TaskStatus.FAILED)
        
        return {
            "workflow_id": workflow_id,
            "total_tasks": len(tasks),
            "completed": completed,
            "failed": failed,
            "pending": len(tasks) - completed - failed,
            "progress": f"{completed}/{len(tasks)}"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_tasks = len(self.task_history)
        completed = sum(1 for t in self.task_history if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.task_history if t.status == TaskStatus.FAILED)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "success_rate": f"{(completed/total_tasks*100):.1f}%" if total_tasks > 0 else "N/A",
            "registered_agents": len(self.agents),
            "active_workflows": len(self.workflows)
        }


if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    
    class MockAgent:
        def execute_task(self, task_type, project_id=None):
            return {"task_type": task_type, "project_id": project_id, "status": "simulated"}
    
    orchestrator.register_agent("langfuse_pm_001", MockAgent())
    
    task_ids = orchestrator.create_daily_pipeline(project_id="demo-project")
    
    tasks = [orchestrator.tasks[tid] for tid in task_ids]
    results = orchestrator.execute_workflow(tasks)
    
    stats = orchestrator.get_statistics()
    print("\n" + "="*60)
    print("📈 执行统计")
    print("="*60)
    for key, value in stats.items():
        print(f"{key:20s}: {value}")

#!/usr/bin/env python3
import sys
import json
from datetime import datetime

sys.path.insert(0, '/Users/viosson')

from agent_system import AgentEmployeeSystem, AgentProfile, AgentRole, setup_default_agents
from agent_orchestrator import AgentOrchestrator, TaskPriority, TaskStatus

print("""
╔═══════════════════════════════════════════════════════════╗
║     DEVOLLEN Agent System - Quick Start Guide            ║
╚═══════════════════════════════════════════════════════════╝
""")

def print_section(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}\n")

def demo_1_basic_system():
    print_section("Demo 1: Basic Agent System")
    system = AgentEmployeeSystem()
    setup_default_agents()
    
    print("Registered Agents:\n")
    for i, agent in enumerate(system.list_agents(), 1):
        print(f"  {i}. {agent.name}")
        print(f"     Role: {agent.role.value}")
        print(f"     Tools: {len(agent.tools)}")
        print()
    
    return system

def demo_2_task_creation():
    print_section("Demo 2: Task Creation and Management")
    from agent_system import AgentStatus
    
    system = AgentEmployeeSystem()
    setup_default_agents()
    agents = system.list_agents()
    
    if agents:
        agent = agents[0]
        print(f"Creating task for '{agent.name}'...\n")
        task = system.create_task(agent.id, "Perform daily monitoring")
        print(f"Task created")
        print(f"  Task ID: {task.id}")
        print(f"  Status: {task.status.value}")
        
        print(f"\nUpdating task status...\n")
        system.update_task_status(
            task.id,
            AgentStatus.COMPLETED,
            result={
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "items_monitored": 15,
                "alerts": 2
            }
        )
        print(f"Task completed")
        print(f"  New status: {task.status.value}")

def demo_3_orchestrator():
    print_section("Demo 3: Agent Orchestrator")
    
    orchestrator = AgentOrchestrator()
    
    class DemoAgent:
        def execute_task(self, task_type, project_id=None):
            return {"task_type": task_type, "project_id": project_id, "status": "completed"}
    
    orchestrator.register_agent("pm_agent", DemoAgent())
    
    print("Creating tasks:\n")
    tasks = [
        ("Project Health Check", "health_check", TaskPriority.HIGH),
        ("Error Analysis", "error_analysis", TaskPriority.NORMAL),
        ("Performance Analysis", "performance_analysis", TaskPriority.NORMAL),
    ]
    
    for task_name, task_type, priority in tasks:
        task = orchestrator.create_task(
            agent_id="pm_agent",
            name=task_name,
            description=f"Execute {task_name}",
            parameters={"type": task_type, "project_id": "demo"},
            priority=priority
        )
        print(f"  ✓ {task_name} (Priority: {priority.name})")
    
    print(f"\nExecuting tasks...\n")
    for task in orchestrator.tasks.values():
        result = orchestrator.execute_task(task.id)
        status = "✓" if result.status.value == "completed" else "✗"
        print(f"  {status} {task.name}: {result.status.value}")
    
    print("\nExecution Statistics:")
    stats = orchestrator.get_statistics()
    for key, value in stats.items():
        print(f"  • {key}: {value}")

def demo_4_daily_pipeline():
    print_section("Demo 4: Daily Workflow Pipeline")
    
    orchestrator = AgentOrchestrator()
    
    class DemoAgent:
        def execute_task(self, task_type, project_id=None):
            return {"task_type": task_type, "status": "completed"}
    
    orchestrator.register_agent("pm_agent", DemoAgent())
    
    print("Creating daily workflow...\n")
    task_ids = orchestrator.create_daily_pipeline(project_id="demo")
    
    print(f"Workflow created ({len(task_ids)} tasks)\n")
    print("Tasks in workflow:\n")
    for i, task_id in enumerate(task_ids, 1):
        task = orchestrator.tasks[task_id]
        print(f"  {i}. {task.name} (Priority: {task.priority.name})")
    
    print(f"\nExecuting workflow...\n")
    tasks = [orchestrator.tasks[tid] for tid in task_ids]
    results = orchestrator.execute_workflow(tasks)
    print("\nWorkflow execution completed")

def main():
    try:
        demo_1_basic_system()
        demo_2_task_creation()
        demo_3_orchestrator()
        demo_4_daily_pipeline()
        
        print_section("Summary")
        print("""
Key Features:
  ✓ Agent Management - Register and manage multiple agents
  ✓ Task Scheduling - Create and track tasks with priorities
  ✓ Workflow Support - Build complex multi-step workflows
  ✓ Real-time Monitoring - Track task status and progress
  ✓ Data Persistence - Save configurations and history

Quick Commands:
  python3 agent_system.py          - Run agent system demo
  python3 agent_orchestrator.py    - Run orchestrator demo
  python3 langfuse_pm_agent.py     - Run PM agent demo
  python3 devollen_agent.py help   - Show CLI help

Next Steps:
  1. Read AGENT_README.md for detailed documentation
  2. Create custom agents for your use cases
  3. Integrate into your application
  4. Set up scheduled workflows

Welcome to DEVOLLEN Agent System!
        """)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

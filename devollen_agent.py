#!/usr/bin/env python3
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Users/viosson')

from agent_system import AgentEmployeeSystem, setup_default_agents
from agent_orchestrator import AgentOrchestrator
from langfuse_pm_agent import LangfuseProjectManagerAgent

class DevOllenAgentManager:
    def __init__(self):
        self.system = AgentEmployeeSystem()
        self.orchestrator = AgentOrchestrator()
        self.agents = {}
        self.config_file = Path("/Users/viosson/agent_manager_config.json")
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                config = json.load(f)
                print(f"Configuration loaded")
        else:
            print("Using default configuration")
    
    def save_config(self):
        config = {
            "agents": [a.id for a in self.agents.values()],
            "saved_at": datetime.now().isoformat()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved")
    
    def initialize(self):
        print("\nInitializing DEVOLLEN Agent System...")
        setup_default_agents()
        pm_agent = LangfuseProjectManagerAgent()
        self.agents["pm"] = pm_agent
        self.orchestrator.register_agent("langfuse_pm_001", pm_agent)
        print("System initialized\n")
        agents_list = self.system.list_agents()
        print(f"Loaded {len(agents_list)} agents:")
        for agent in agents_list:
            print(f"   • {agent.name}")
        self.save_config()
    
    def list_agents(self):
        print("\nRegistered Agents:\n")
        agents = self.system.list_agents()
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent.name}")
            print(f"     ID: {agent.id}")
            print(f"     Role: {agent.role.value}")
            print(f"     Tools: {len(agent.tools)}")
            print()
    
    def generate_report(self, project_id: str = None):
        print("\nGenerating Langfuse project report...\n")
        if "pm" in self.agents:
            result = self.agents["pm"].generate_daily_report(project_id)
            print("\nReport generation completed\n")
        else:
            print("PM Agent not initialized")
    
    def create_daily_pipeline(self, project_id: str = None):
        print("\nCreating daily workflow...\n")
        if "pm" in self.agents:
            self.orchestrator.register_agent("langfuse_pm_001", self.agents["pm"])
        task_ids = self.orchestrator.create_daily_pipeline(project_id)
        print(f"\nWorkflow created ({len(task_ids)} tasks)\n")
        print("Workflow tasks:\n")
        for i, task_id in enumerate(task_ids, 1):
            task = self.orchestrator.tasks[task_id]
            print(f"  {i}. {task.name}")
            print(f"     Priority: {task.priority.name}")
        return task_ids
    
    def execute_workflow(self, task_ids: list = None):
        print("\nExecuting workflow...\n")
        if not task_ids:
            task_ids = list(self.orchestrator.tasks.keys())
        if not task_ids:
            print("No tasks to execute")
            return
        tasks = [self.orchestrator.tasks[tid] for tid in task_ids]
        results = self.orchestrator.execute_workflow(tasks)
        stats = self.orchestrator.get_statistics()
        print("\nWorkflow execution completed\n")
        print("Execution statistics:")
        for key, value in stats.items():
            print(f"  • {key}: {value}")
    
    def check_health(self, project_id: str = None):
        print("\nChecking project health...\n")
        if "pm" in self.agents:
            result = self.agents["pm"].check_health(project_id)
            if isinstance(result, dict) and "result" in result:
                health = result["result"]
                print(f"  • Status: {health.get('status', 'unknown')}")
                print(f"  • Error count: {health.get('error_count', 0)}")
        else:
            print("PM Agent not initialized")
    
    def analyze_errors(self, project_id: str = None):
        print("\nAnalyzing project errors...\n")
        if "pm" in self.agents:
            result = self.agents["pm"].analyze_errors(project_id)
            if isinstance(result, dict) and "result" in result:
                error_data = result["result"]
                print(f"  • Total errors: {error_data.get('error_count', 0)}")
        else:
            print("PM Agent not initialized")
    
    def show_statistics(self):
        print("\nSystem Statistics:\n")
        stats = self.orchestrator.get_statistics()
        print("  Executed tasks:")
        print(f"    • Total: {stats.get('total_tasks', 0)}")
        print(f"    • Completed: {stats.get('completed_tasks', 0)}")
        print(f"    • Failed: {stats.get('failed_tasks', 0)}")
        print(f"    • Success rate: {stats.get('success_rate', 'N/A')}")
        print(f"\n  System resources:")
        print(f"    • Registered agents: {stats.get('registered_agents', 0)}")
        print(f"    • Active workflows: {stats.get('active_workflows', 0)}")
    
    def show_menu(self):
        print("""
DEVOLLEN Agent System Manager

Available commands:

  System Management:
    init              Initialize system
    list              List all agents
    stats             Show statistics

  Project Monitoring:
    health            Check project health
    errors            Analyze project errors
    report            Generate project report
    
  Workflow:
    pipeline          Create daily workflow
    execute           Execute pending tasks

  Other:
    help              Show this menu
    exit              Exit program
        """)

def main():
    parser = argparse.ArgumentParser(description="DEVOLLEN Agent System Manager")
    parser.add_argument("command", nargs="?", default="help", help="Command to execute")
    parser.add_argument("--project", "-p", help="Project ID")
    args = parser.parse_args()
    
    manager = DevOllenAgentManager()
    command = args.command.lower()
    
    if command == "init":
        manager.initialize()
    elif command == "list":
        manager.list_agents()
    elif command == "health":
        manager.check_health(args.project)
    elif command == "errors":
        manager.analyze_errors(args.project)
    elif command == "report":
        manager.generate_report(args.project)
    elif command == "pipeline":
        task_ids = manager.create_daily_pipeline(args.project)
        manager.execute_workflow(task_ids)
    elif command == "execute":
        manager.execute_workflow()
    elif command == "stats":
        manager.show_statistics()
    elif command in ("help", "-h", "--help"):
        manager.show_menu()
    elif command == "exit":
        print("\nGoodbye!")
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print("Type 'help' to see available commands")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

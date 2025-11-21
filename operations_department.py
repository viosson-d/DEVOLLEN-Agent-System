"""
运维部门架构定义
Operations Department - 负责所有工具和系统的运维管理
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass


# ============= 运维部门定义 =============
class OperationsDepartment:
    """运维部门"""
    
    DEPT_ID = "operations_dept"
    DEPT_NAME = "运维部门"
    DEPT_NAME_EN = "Operations Department"
    DEPT_TYPE = "OPERATIONS"
    
    DESCRIPTION = """
    运维部门负责所有外部工具和系统的运维管理工作。
    每个工具都有专门的管理专家负责操作、监控和维护。
    """
    
    RESPONSIBILITIES = [
        "工具系统运维",
        "操作日志记录",
        "错误监控处理",
        "性能优化",
        "工具集成管理"
    ]


# ============= 职位定义 =============
class OperationsPositions:
    """运维部门的职位"""
    
    # 1. 工具操作执行员（初级）
    TOOL_OPERATOR = {
        "name": "Tool Operator",
        "name_cn": "工具操作执行员",
        "level": "JUNIOR",
        "max_agents": 5,
        "required_skills": [
            "tool_invocation",
            "basic_logging",
            "error_reporting"
        ],
        "responsibilities": [
            "执行工具操作命令",
            "记录基本操作日志",
            "报告错误信息"
        ]
    }
    
    # 2. Langfuse 管理专家（高级）
    LANGFUSE_MANAGER = {
        "name": "Langfuse Operations Manager",
        "name_cn": "Langfuse 管理专家",
        "level": "SENIOR",
        "max_agents": 2,
        "required_skills": [
            "langfuse_api",
            "trace_analysis",
            "performance_monitoring",
            "error_diagnosis",
            "interaction_logging"
        ],
        "responsibilities": [
            "管理 Langfuse 所有操作",
            "记录每次 Langfuse 交互",
            "分析 Trace 数据",
            "生成性能报告",
            "处理 Langfuse 错误"
        ],
        "managed_tool": "langfuse"
    }
    
    # 3. GitHub 管理专家（高级）
    GITHUB_MANAGER = {
        "name": "GitHub Operations Manager",
        "name_cn": "GitHub 管理专家",
        "level": "SENIOR",
        "max_agents": 2,
        "required_skills": [
            "github_api",
            "repository_management",
            "code_operations",
            "interaction_logging"
        ],
        "responsibilities": [
            "管理 GitHub 所有操作",
            "记录每次 GitHub 交互",
            "仓库管理",
            "代码操作追踪",
            "处理 GitHub 错误"
        ],
        "managed_tool": "github"
    }
    
    # 4. Slack 管理专家（高级）
    SLACK_MANAGER = {
        "name": "Slack Operations Manager",
        "name_cn": "Slack 管理专家",
        "level": "SENIOR",
        "max_agents": 2,
        "required_skills": [
            "slack_api",
            "message_management",
            "channel_operations",
            "interaction_logging"
        ],
        "responsibilities": [
            "管理 Slack 所有操作",
            "记录每次 Slack 交互",
            "消息管理",
            "频道操作",
            "处理 Slack 错误"
        ],
        "managed_tool": "slack"
    }
    
    # 5. 数据库管理专家（高级）
    DATABASE_MANAGER = {
        "name": "Database Operations Manager",
        "name_cn": "数据库管理专家",
        "level": "SENIOR",
        "max_agents": 2,
        "required_skills": [
            "database_operations",
            "query_optimization",
            "data_integrity",
            "interaction_logging"
        ],
        "responsibilities": [
            "管理数据库所有操作",
            "记录每次数据库交互",
            "查询优化",
            "数据完整性检查",
            "处理数据库错误"
        ],
        "managed_tool": "database"
    }
    
    # 6. 运维总监（负责人）
    OPERATIONS_LEAD = {
        "name": "Operations Lead",
        "name_cn": "运维总监",
        "level": "LEAD",
        "max_agents": 1,
        "required_skills": [
            "all_tools_knowledge",
            "team_coordination",
            "strategic_planning",
            "incident_management"
        ],
        "responsibilities": [
            "协调所有工具使用",
            "制定运维策略",
            "处理重大事故",
            "优化工具集成",
            "团队管理"
        ]
    }
    
    @classmethod
    def get_all_positions(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有职位"""
        return {
            "Tool Operator": cls.TOOL_OPERATOR,
            "Langfuse Operations Manager": cls.LANGFUSE_MANAGER,
            "GitHub Operations Manager": cls.GITHUB_MANAGER,
            "Slack Operations Manager": cls.SLACK_MANAGER,
            "Database Operations Manager": cls.DATABASE_MANAGER,
            "Operations Lead": cls.OPERATIONS_LEAD
        }
    
    @classmethod
    def get_manager_by_tool(cls, tool_name: str) -> Dict[str, Any]:
        """根据工具名称获取对应的管理专家职位"""
        tool_position_map = {
            "langfuse": cls.LANGFUSE_MANAGER,
            "github": cls.GITHUB_MANAGER,
            "slack": cls.SLACK_MANAGER,
            "database": cls.DATABASE_MANAGER
        }
        return tool_position_map.get(tool_name.lower())


# ============= Agent 示例 =============
class SampleOperationsAgents:
    """运维部门示例 Agent"""
    
    # Langfuse 管理专家示例
    LANGFUSE_MANAGER_001 = {
        "agent_id": "langfuse_mgr_001",
        "agent_name": "张三 - Langfuse 管理专家",
        "position": "Langfuse Operations Manager",
        "skills": [
            "langfuse_api",
            "trace_analysis",
            "performance_monitoring",
            "error_diagnosis",
            "interaction_logging"
        ],
        "managed_tool": "langfuse",
        "experience_years": 3
    }
    
    # GitHub 管理专家示例
    GITHUB_MANAGER_001 = {
        "agent_id": "github_mgr_001",
        "agent_name": "李四 - GitHub 管理专家",
        "position": "GitHub Operations Manager",
        "skills": [
            "github_api",
            "repository_management",
            "code_operations",
            "interaction_logging"
        ],
        "managed_tool": "github",
        "experience_years": 4
    }
    
    # Slack 管理专家示例
    SLACK_MANAGER_001 = {
        "agent_id": "slack_mgr_001",
        "agent_name": "王五 - Slack 管理专家",
        "position": "Slack Operations Manager",
        "skills": [
            "slack_api",
            "message_management",
            "channel_operations",
            "interaction_logging"
        ],
        "managed_tool": "slack",
        "experience_years": 2
    }
    
    # 运维总监示例
    OPERATIONS_LEAD_001 = {
        "agent_id": "ops_lead_001",
        "agent_name": "赵六 - 运维总监",
        "position": "Operations Lead",
        "skills": [
            "all_tools_knowledge",
            "team_coordination",
            "strategic_planning",
            "incident_management"
        ],
        "experience_years": 5
    }


# ============= 工作流示例 =============
class OperationsWorkflow:
    """运维部门工作流"""
    
    @staticmethod
    def get_workflow_example():
        """获取工作流示例"""
        return """
        运维部门工作流:
        
        1. 用户请求 → 运维总监接收
           ↓
        2. 运维总监分配 → 对应工具的管理专家
           ↓
        3. 工具管理专家执行操作
           - 调用工具 API
           - 记录每次交互到日志
           - 处理错误和重试
           ↓
        4. 返回结果 → 运维总监
           ↓
        5. 运维总监汇总 → 返回给用户
        
        示例:
        
        【场景 1】: 查询 Langfuse 项目状态
        - 运维总监收到请求
        - 分配给 Langfuse 管理专家
        - Langfuse 管理专家:
          * 执行 get_projects API
          * 记录交互: tool_operations.jsonl
          * 返回结果
        - 运维总监汇总返回
        
        【场景 2】: 同时操作多个工具
        - 运维总监收到请求
        - 并行分配给:
          * Langfuse 管理专家
          * GitHub 管理专家
        - 各管理专家执行操作并记录
        - 运维总监汇总所有结果返回
        """


# ============= 测试 =============
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏢 运维部门架构")
    print("="*60)
    
    dept = OperationsDepartment()
    print(f"\n部门: {dept.DEPT_NAME} ({dept.DEPT_NAME_EN})")
    print(f"类型: {dept.DEPT_TYPE}")
    print(f"\n部门职责:")
    for r in dept.RESPONSIBILITIES:
        print(f"  • {r}")
    
    print("\n" + "="*60)
    print("📋 部门职位")
    print("="*60)
    
    positions = OperationsPositions.get_all_positions()
    for pos_name, pos_info in positions.items():
        print(f"\n【{pos_info['name_cn']}】({pos_info['name']})")
        print(f"  级别: {pos_info['level']}")
        print(f"  人数上限: {pos_info['max_agents']}")
        print(f"  职责:")
        for r in pos_info['responsibilities']:
            print(f"    - {r}")
        if 'managed_tool' in pos_info:
            print(f"  负责工具: {pos_info['managed_tool']}")
    
    print("\n" + "="*60)
    print("👥 示例 Agent")
    print("="*60)
    
    agents = SampleOperationsAgents()
    for agent_name in ['LANGFUSE_MANAGER_001', 'GITHUB_MANAGER_001', 
                       'SLACK_MANAGER_001', 'OPERATIONS_LEAD_001']:
        agent = getattr(agents, agent_name)
        print(f"\n  • {agent['agent_name']}")
        print(f"    职位: {agent['position']}")
        if 'managed_tool' in agent:
            print(f"    负责工具: {agent['managed_tool']}")
    
    print("\n" + "="*60)
    print("🔄 工作流")
    print("="*60)
    print(OperationsWorkflow.get_workflow_example())
    
    print("\n" + "="*60)
    print("✅ 这是一个完整的运维部门架构")
    print("="*60 + "\n")

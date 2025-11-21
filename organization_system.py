"""  
Integrated Organization System
综合组织管理系统 - 部门 + Unit + Agent 三层一体
"""

from typing import Dict, List, Optional, Any
from agent_department import (
    DepartmentSystem, Department, DepartmentType, Position, 
    PositionLevel, AgentInPosition, PREDEFINED_POSITIONS
)
from agent_unit import (
    UnitManager, AgentUnit, UnitMember, UnitRole, UnitStatus
)
import json
from datetime import datetime


class OrganizationSystem:
    """综合组织管理系统"""
    
    def __init__(self):
        self.department_system = DepartmentSystem()
        self.unit_manager = UnitManager()
    
    # ==================== 部门管理 ====================
    
    def create_department_with_positions(
        self,
        dept_id: str,
        name: str,
        dept_type: DepartmentType,
        description: str,
        lead_agent_id: str,
        lead_agent_name: str,
        position_names: Optional[List[str]] = None
    ) -> Optional[Department]:
        """创建部门并配置职位"""
        dept = self.department_system.create_department(
            dept_id=dept_id,
            name=name,
            dept_type=dept_type,
            description=description,
            lead_agent_id=lead_agent_id,
            lead_agent_name=lead_agent_name
        )
        
        if not dept:
            return None
        
        # 添加预定义职位
        if position_names:
            dept_positions = PREDEFINED_POSITIONS.get(dept_type.value, {})
            for pos_name in position_names:
                if pos_name in dept_positions:
                    self.department_system.add_position_to_department(
                        dept_id,
                        dept_positions[pos_name]
                    )
        
        return dept
    
    def list_departments(self, dept_type: Optional[DepartmentType] = None) -> List[Dict]:
        """列出部门（支持类型过滤）"""
        if dept_type:
            depts = self.department_system.list_departments_by_type(dept_type)
        else:
            depts = self.department_system.list_departments()
        
        return [
            {
                "id": d.id,
                "name": d.name,
                "type": d.type.value,
                "lead": d.lead_agent_name,
                "total_agents": len(d.get_all_agents()),
                "available_agents": len(d.get_available_agents()),
                "positions": list(d.positions.keys())
            }
            for d in depts
        ]
    
    def add_agent_to_department(
        self,
        dept_id: str,
        agent_id: str,
        agent_name: str,
        position_name: str,
        skills: List[str]
    ) -> bool:
        """添加 Agent 到部门"""
        dept = self.department_system.get_department(dept_id)
        if not dept:
            print(f"❌ 部门 {dept_id} 不存在")
            return False
        
        if position_name not in dept.positions:
            print(f"❌ 职位 '{position_name}' 不存在于部门 '{dept.name}'")
            return False
        
        # 获取位置的职位对象
        if dept.positions[position_name]:
            position = dept.positions[position_name][0].position
        else:
            # 从预定义职位获取
            dept_type_name = dept.type.value if hasattr(dept.type, 'value') else str(dept.type)
            position = PREDEFINED_POSITIONS.get(dept_type_name, {}).get(position_name)
            if not position:
                print(f"❌ 无法获取职位信息")
                return False
        
        agent = AgentInPosition(
            agent_id=agent_id,
            agent_name=agent_name,
            position=position,
            department_id=dept_id,
            skills=skills
        )
        
        return self.department_system.add_agent_to_department(dept_id, agent)
    
    # ==================== Unit 管理 ====================
    
    def create_unit_from_agents(
        self,
        unit_id: str,
        name: str,
        description: str,
        lead_agent_id: str,
        project_id: Optional[str] = None,
        priority: int = 0
    ) -> Optional[AgentUnit]:
        """创建 Unit（指定负责人）"""
        lead_agent = self.department_system.get_agent_by_id(lead_agent_id)
        if not lead_agent:
            print(f"❌ Agent {lead_agent_id} 不存在")
            return None
        
        lead_member = UnitMember(
            agent_id=lead_agent.agent_id,
            agent_name=lead_agent.agent_name,
            role=UnitRole.LEAD,
            department_id=lead_agent.department_id,
            position_name=lead_agent.position.name,
            skills=lead_agent.skills,
            responsibilities="单位负责人，协调和决策"
        )
        
        unit = self.unit_manager.create_unit(
            unit_id=unit_id,
            name=name,
            description=description,
            lead_member=lead_member,
            project_id=project_id,
            priority=priority
        )
        
        if unit:
            # 分配负责人到 Unit
            self.department_system.assign_agent_to_unit(lead_agent_id, unit_id)
        
        return unit
    
    def add_executor_to_unit(
        self,
        unit_id: str,
        agent_id: str,
        responsibilities: str = ""
    ) -> bool:
        """添加执行者到 Unit"""
        agent = self.department_system.get_agent_by_id(agent_id)
        if not agent:
            print(f"❌ Agent {agent_id} 不存在")
            return False
        
        unit = self.unit_manager.get_unit(unit_id)
        if not unit:
            print(f"❌ Unit {unit_id} 不存在")
            return False
        
        member = UnitMember(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            role=UnitRole.EXECUTOR,
            department_id=agent.department_id,
            position_name=agent.position.name,
            skills=agent.skills,
            responsibilities=responsibilities
        )
        
        result = self.unit_manager.add_member_to_unit(unit_id, member, UnitRole.EXECUTOR)
        
        if result:
            # 分配 Agent 到 Unit
            self.department_system.assign_agent_to_unit(agent_id, unit_id)
        
        return result
    
    def add_supporter_to_unit(
        self,
        unit_id: str,
        agent_id: str,
        responsibilities: str = ""
    ) -> bool:
        """添加支持者到 Unit"""
        agent = self.department_system.get_agent_by_id(agent_id)
        if not agent:
            print(f"❌ Agent {agent_id} 不存在")
            return False
        
        unit = self.unit_manager.get_unit(unit_id)
        if not unit:
            print(f"❌ Unit {unit_id} 不存在")
            return False
        
        member = UnitMember(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            role=UnitRole.SUPPORTER,
            department_id=agent.department_id,
            position_name=agent.position.name,
            skills=agent.skills,
            responsibilities=responsibilities
        )
        
        result = self.unit_manager.add_member_to_unit(unit_id, member, UnitRole.SUPPORTER)
        
        if result:
            # 分配 Agent 到 Unit
            self.department_system.assign_agent_to_unit(agent_id, unit_id)
        
        return result
    
    # ==================== 查询功能 ====================
    
    def find_agents_for_unit(
        self,
        skills: Optional[List[str]] = None,
        position_level: Optional[PositionLevel] = None,
        dept_type: Optional[DepartmentType] = None,
        limit: Optional[int] = None,
        available_only: bool = True
    ) -> List[Dict]:
        """查找适合加入 Unit 的 Agent（可用的、符合条件的）"""
        agents = self.department_system.search_agents(
            skills=skills,
            position_level=position_level,
            available_only=available_only,
            dept_type=dept_type
        )
        
        if limit:
            agents = agents[:limit]
        
        return [
            {
                "agent_id": a.agent_id,
                "agent_name": a.agent_name,
                "department": a.department_id,
                "position": a.position.name,
                "level": a.position.level.value,
                "skills": a.skills,
                "available": a.availability
            }
            for a in agents
        ]
    
    def get_unit_info(self, unit_id: str) -> Optional[Dict]:
        """获取 Unit 详细信息"""
        unit = self.unit_manager.get_unit(unit_id)
        if not unit:
            return None
        
        return {
            "id": unit.id,
            "name": unit.name,
            "description": unit.description,
            "project_id": unit.project_id,
            "status": unit.status.value,
            "priority": unit.priority,
            "lead": {
                "agent_id": unit.lead_member.agent_id,
                "agent_name": unit.lead_member.agent_name,
                "department": unit.lead_member.department_id,
                "position": unit.lead_member.position_name
            } if unit.lead_member else None,
            "executors": [
                {
                    "agent_id": m.agent_id,
                    "agent_name": m.agent_name,
                    "department": m.department_id,
                    "position": m.position_name,
                    "responsibilities": m.responsibilities
                }
                for m in unit.executor_members
            ],
            "supporters": [
                {
                    "agent_id": m.agent_id,
                    "agent_name": m.agent_name,
                    "department": m.department_id,
                    "position": m.position_name,
                    "responsibilities": m.responsibilities
                }
                for m in unit.supporter_members
            ],
            "member_count": unit.get_member_count(),
            "tasks_count": len(unit.tasks),
            "created_at": unit.created_at,
            "started_at": unit.started_at
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """查看 Agent 状态"""
        agent = self.department_system.get_agent_by_id(agent_id)
        if not agent:
            return None
        
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.agent_name,
            "department": agent.department_id,
            "position": agent.position.name,
            "level": agent.position.level.value,
            "skills": agent.skills,
            "availability": agent.availability,
            "assigned_unit_id": agent.assigned_unit_id,
            "joined_at": agent.joined_at
        }
    
    # ==================== 释放和清理 ====================
    
    def release_agent_from_unit(self, agent_id: str) -> bool:
        """从 Unit 释放 Agent 回到部门"""
        result = self.department_system.release_agent_from_unit(agent_id)
        if result:
            print(f"✓ Agent 已释放，返回部门")
        return result
    
    def disband_unit(self, unit_id: str) -> bool:
        """解散 Unit 并释放所有成员"""
        unit = self.unit_manager.get_unit(unit_id)
        if not unit:
            return False
        
        # 释放所有成员
        for member in unit.get_all_members():
            self.department_system.release_agent_from_unit(member.agent_id)
        
        # 解散 Unit
        result = self.unit_manager.disband_unit(unit_id)
        return result
    
    # ==================== 统计和报告 ====================
    
    def get_organization_status(self) -> Dict[str, Any]:
        """获取组织总体状态"""
        dept_stats = self.department_system.get_statistics()
        unit_stats = self.unit_manager.get_statistics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "departments": dept_stats,
            "units": unit_stats,
            "summary": {
                "total_departments": dept_stats["total_departments"],
                "total_agents": dept_stats["total_agents"],
                "available_agents": dept_stats["available_agents"],
                "assigned_agents": dept_stats["assigned_agents"],
                "total_units": unit_stats["total_units"],
                "active_units": unit_stats["active_units"],
                "utilization_rate": f"{(unit_stats['total_members'] / max(dept_stats['total_agents'], 1) * 100):.1f}%"
            }
        }
    
    def generate_report(self) -> str:
        """生成组织状态报告"""
        status = self.get_organization_status()
        
        report = f"""
╔════════════════════════════════════════════════════════════╗
║          组织系统状态报告 | {status['timestamp']}
╚════════════════════════════════════════════════════════════╝

【部门信息】
  • 总部门数: {status['summary']['total_departments']}
  • 部门列表:
"""
        for dept_id, dept_info in status['departments']['departments'].items():
            report += f"    - {dept_info['name']} ({dept_info['type']}): {dept_info['total_agents']} 个 Agent\n"
        
        report += f"""
【人员情况】
  • 总人数: {status['summary']['total_agents']}
  • 可用人数: {status['summary']['available_agents']}
  • 已分配人数: {status['summary']['assigned_agents']}
  • 人力利用率: {status['summary']['utilization_rate']}

【Unit 信息】
  • 总 Unit 数: {status['summary']['total_units']}
  • 活跃 Unit: {status['summary']['active_units']}
  • 成员总数: {status['units']['total_members']}
  • 任务总数: {status['units']['total_tasks']}
  • Unit 状态分布:
"""
        for status_type, count in status['units']['units_by_status'].items():
            report += f"    - {status_type}: {count}\n"
        
        report += "\n╚════════════════════════════════════════════════════════════╝\n"
        return report


# 便捷初始化函数
def setup_default_organization():
    """设置默认组织结构"""
    org = OrganizationSystem()
    
    # 创建部门并添加职位
    org.create_department_with_positions(
        dept_id="pm_dept",
        name="项目管理部",
        dept_type=DepartmentType.MANAGEMENT,
        description="负责所有项目的规划和管理",
        lead_agent_id="pm_lead_001",
        lead_agent_name="项目管理总监",
        position_names=[]  # 暂时不添加职位
    )
    
    org.create_department_with_positions(
        dept_id="tech_dept",
        name="技术部",
        dept_type=DepartmentType.TECHNOLOGY,
        description="负责技术实现和系统开发",
        lead_agent_id="tech_lead_001",
        lead_agent_name="技术总监",
        position_names=["Senior Developer", "Junior Developer", "Tech Lead"]
    )
    
    org.create_department_with_positions(
        dept_id="data_dept",
        name="数据部",
        dept_type=DepartmentType.DATA,
        description="负责数据分析和业务洞察",
        lead_agent_id="data_lead_001",
        lead_agent_name="数据总监",
        position_names=["Senior Analyst", "Junior Analyst", "Data Lead"]
    )
    
    # 为项目管理部添加职位
    org.department_system.add_position_to_department(
        "pm_dept",
        PREDEFINED_POSITIONS["pm"]["Senior PM"]
    )
    org.department_system.add_position_to_department(
        "pm_dept",
        PREDEFINED_POSITIONS["pm"]["PM Lead"]
    )
    
    print("✓ 默认组织结构已创建")
    return org

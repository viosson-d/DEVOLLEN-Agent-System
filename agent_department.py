"""  
Agent Department System
部门管理系统 - 组织 Agent 的部门结构
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import json


class PositionLevel(Enum):
    """职位等级"""
    INTERN = "intern"              # 实习生
    JUNIOR = "junior"              # 初级
    SENIOR = "senior"              # 高级
    LEAD = "lead"                  # 负责人
    MANAGER = "manager"            # 经理


class DepartmentType(Enum):
    """部门类型"""
    MANAGEMENT = "management"      # 管理部门
    TECHNOLOGY = "technology"      # 技术部门
    DATA = "data"                  # 数据部门
    PRODUCT = "product"            # 产品部门
    OPERATIONS = "operations"      # 运维部门


@dataclass
class Position:
    """职位定义"""
    name: str                       # "Senior Developer"
    level: PositionLevel            # 职位等级
    description: str                # 职位描述
    required_skills: List[str] = field(default_factory=list)  # 需要的技能
    max_agents: int = 5             # 最多可配置的 Agent 数量
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "level": self.level.value,
            "description": self.description,
            "required_skills": self.required_skills,
            "max_agents": self.max_agents
        }


@dataclass
class AgentInPosition:
    """职位上的 Agent"""
    agent_id: str
    agent_name: str
    position: Position
    department_id: str
    skills: List[str] = field(default_factory=list)
    availability: bool = True      # 是否可用（未被分配到 Unit）
    assigned_unit_id: Optional[str] = None  # 当前所属 Unit
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "position": self.position.to_dict(),
            "department_id": self.department_id,
            "skills": self.skills,
            "availability": self.availability,
            "assigned_unit_id": self.assigned_unit_id,
            "joined_at": self.joined_at
        }


@dataclass
class Department:
    """部门"""
    id: str
    name: str
    type: DepartmentType
    description: str
    lead_agent_id: str              # 部长 Agent ID
    lead_agent_name: str            # 部长 Agent 名称
    
    # 组织结构
    positions: Dict[str, List[AgentInPosition]] = field(default_factory=dict)
    # positions 结构: {"Senior Developer": [agent1, agent2], ...}
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_position(self, position: Position) -> bool:
        """添加职位"""
        if position.name in self.positions:
            return False
        self.positions[position.name] = []
        self.updated_at = datetime.now().isoformat()
        return True
    
    def add_agent_to_position(self, agent: AgentInPosition) -> bool:
        """添加 Agent 到职位"""
        position_name = agent.position.name
        if position_name not in self.positions:
            return False
        
        if len(self.positions[position_name]) >= agent.position.max_agents:
            return False
        
        self.positions[position_name].append(agent)
        self.updated_at = datetime.now().isoformat()
        return True
    
    def remove_agent_from_position(self, agent_id: str, position_name: str) -> bool:
        """从职位移除 Agent"""
        if position_name not in self.positions:
            return False
        
        self.positions[position_name] = [
            a for a in self.positions[position_name] 
            if a.agent_id != agent_id
        ]
        self.updated_at = datetime.now().isoformat()
        return True
    
    def get_all_agents(self) -> List[AgentInPosition]:
        """获取部门所有 Agent"""
        all_agents = []
        for agents_in_position in self.positions.values():
            all_agents.extend(agents_in_position)
        return all_agents
    
    def get_available_agents(self) -> List[AgentInPosition]:
        """获取部门可用 Agent（未被分配到 Unit）"""
        return [a for a in self.get_all_agents() if a.availability]
    
    def get_agents_by_position(self, position_name: str) -> List[AgentInPosition]:
        """按职位获取 Agent"""
        return self.positions.get(position_name, [])
    
    def get_agents_by_skill(self, skill: str) -> List[AgentInPosition]:
        """按技能获取 Agent"""
        return [
            a for a in self.get_all_agents() 
            if skill in a.skills
        ]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "lead_agent_id": self.lead_agent_id,
            "lead_agent_name": self.lead_agent_name,
            "positions": {
                pos_name: [a.to_dict() for a in agents]
                for pos_name, agents in self.positions.items()
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class DepartmentSystem:
    """部门管理系统"""
    
    def __init__(self, storage_file: str = "/Users/viosson/departments_config.json"):
        self.storage_file = storage_file
        self.departments: Dict[str, Department] = {}
        self.load_departments()
    
    def create_department(
        self, 
        dept_id: str,
        name: str,
        dept_type: DepartmentType,
        description: str,
        lead_agent_id: str,
        lead_agent_name: str
    ) -> Optional[Department]:
        """创建部门"""
        if dept_id in self.departments:
            print(f"⚠️ 部门 {dept_id} 已存在")
            return None
        
        dept = Department(
            id=dept_id,
            name=name,
            type=dept_type,
            description=description,
            lead_agent_id=lead_agent_id,
            lead_agent_name=lead_agent_name
        )
        
        self.departments[dept_id] = dept
        self.save_departments()
        print(f"✓ 部门 '{name}' 创建成功 (负责人: {lead_agent_name})")
        return dept
    
    def get_department(self, dept_id: str) -> Optional[Department]:
        """获取部门"""
        return self.departments.get(dept_id)
    
    def list_departments(self) -> List[Department]:
        """列出所有部门"""
        return list(self.departments.values())
    
    def list_departments_by_type(self, dept_type: DepartmentType) -> List[Department]:
        """按类型列出部门"""
        return [d for d in self.departments.values() if d.type == dept_type]
    
    def add_position_to_department(
        self,
        dept_id: str,
        position: Position
    ) -> bool:
        """添加职位到部门"""
        dept = self.get_department(dept_id)
        if not dept:
            return False
        
        if position.name in dept.positions:
            return True  # 职位已存在
        
        dept.positions[position.name] = []
        dept.updated_at = datetime.now().isoformat()
        self.save_departments()
        print(f"✓ 职位 '{position.name}' 已添加到部门 '{dept.name}'")
        return True
    
    def add_agent_to_department(
        self,
        dept_id: str,
        agent: AgentInPosition
    ) -> bool:
        """添加 Agent 到部门"""
        dept = self.get_department(dept_id)
        if not dept:
            return False
        
        result = dept.add_agent_to_position(agent)
        if result:
            self.save_departments()
            print(f"✓ Agent '{agent.agent_name}' 已添加到部门 '{dept.name}' (职位: {agent.position.name})")
        return result
    
    def assign_agent_to_unit(
        self,
        agent_id: str,
        unit_id: str
    ) -> bool:
        """将 Agent 分配到 Unit"""
        for dept in self.departments.values():
            for agents_list in dept.positions.values():
                for agent in agents_list:
                    if agent.agent_id == agent_id:
                        agent.availability = False
                        agent.assigned_unit_id = unit_id
                        self.save_departments()
                        print(f"✓ Agent '{agent.agent_name}' 已分配到 Unit '{unit_id}'")
                        return True
        return False
    
    def release_agent_from_unit(self, agent_id: str) -> bool:
        """将 Agent 从 Unit 释放回部门"""
        for dept in self.departments.values():
            for agents_list in dept.positions.values():
                for agent in agents_list:
                    if agent.agent_id == agent_id:
                        agent.availability = True
                        agent.assigned_unit_id = None
                        self.save_departments()
                        print(f"✓ Agent '{agent.agent_name}' 已从 Unit 释放")
                        return True
        return False
    
    def get_agent_by_id(self, agent_id: str) -> Optional[AgentInPosition]:
        """按 ID 查找 Agent"""
        for dept in self.departments.values():
            for agents_list in dept.positions.values():
                for agent in agents_list:
                    if agent.agent_id == agent_id:
                        return agent
        return None
    
    def search_agents(
        self,
        skills: Optional[List[str]] = None,
        position_level: Optional[PositionLevel] = None,
        available_only: bool = False,
        dept_type: Optional[DepartmentType] = None
    ) -> List[AgentInPosition]:
        """搜索 Agent"""
        results = []
        
        for dept in self.departments.values():
            # 按部门类型过滤
            if dept_type and dept.type != dept_type:
                continue
            
            for agents_list in dept.positions.values():
                for agent in agents_list:
                    # 按可用性过滤
                    if available_only and not agent.availability:
                        continue
                    
                    # 按职位等级过滤
                    if position_level and agent.position.level != position_level:
                        continue
                    
                    # 按技能过滤
                    if skills:
                        if not any(skill in agent.skills for skill in skills):
                            continue
                    
                    results.append(agent)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_agents = 0
        available_agents = 0
        assigned_agents = 0
        
        for dept in self.departments.values():
            dept_agents = dept.get_all_agents()
            total_agents += len(dept_agents)
            available_agents += len(dept.get_available_agents())
            assigned_agents += len([a for a in dept_agents if not a.availability])
        
        return {
            "total_departments": len(self.departments),
            "total_agents": total_agents,
            "available_agents": available_agents,
            "assigned_agents": assigned_agents,
            "departments": {
                dept_id: {
                    "name": dept.name,
                    "type": dept.type.value,
                    "total_agents": len(dept.get_all_agents()),
                    "available_agents": len(dept.get_available_agents())
                }
                for dept_id, dept in self.departments.items()
            }
        }
    
    def save_departments(self):
        """保存部门配置"""
        data = {
            dept_id: dept.to_dict()
            for dept_id, dept in self.departments.items()
        }
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存部门配置失败: {e}")
    
    def load_departments(self):
        """加载部门配置"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for dept_id, dept_data in data.items():
                dept = Department(
                    id=dept_data["id"],
                    name=dept_data["name"],
                    type=DepartmentType(dept_data["type"]),
                    description=dept_data["description"],
                    lead_agent_id=dept_data["lead_agent_id"],
                    lead_agent_name=dept_data["lead_agent_name"],
                    created_at=dept_data.get("created_at"),
                    updated_at=dept_data.get("updated_at")
                )
                
                # 恢复职位和 Agent
                for pos_name, agents_data in dept_data.get("positions", {}).items():
                    # 恢复职位（从第一个 agent 的数据中取）
                    if agents_data:
                        first_agent_pos_data = agents_data[0]["position"]
                        position = Position(
                            name=first_agent_pos_data["name"],
                            level=PositionLevel(first_agent_pos_data["level"]),
                            description=first_agent_pos_data["description"],
                            required_skills=first_agent_pos_data["required_skills"],
                            max_agents=first_agent_pos_data["max_agents"]
                        )
                        dept.add_position(position)
                        
                        # 恢复 Agent
                        for agent_data in agents_data:
                            agent = AgentInPosition(
                                agent_id=agent_data["agent_id"],
                                agent_name=agent_data["agent_name"],
                                position=position,
                                department_id=agent_data["department_id"],
                                skills=agent_data["skills"],
                                availability=agent_data["availability"],
                                assigned_unit_id=agent_data.get("assigned_unit_id"),
                                joined_at=agent_data["joined_at"]
                            )
                            dept.positions[pos_name].append(agent)
                
                self.departments[dept_id] = dept
        
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ 加载部门配置失败: {e}")


# 预定义职位
PREDEFINED_POSITIONS = {
    "pm": {
        "Senior PM": Position(
            name="Senior PM",
            level=PositionLevel.SENIOR,
            description="高级项目经理",
            required_skills=["project_management", "leadership", "communication"],
            max_agents=3
        ),
        "PM Lead": Position(
            name="PM Lead",
            level=PositionLevel.LEAD,
            description="项目经理负责人",
            required_skills=["project_management", "leadership", "strategy"],
            max_agents=1
        ),
    },
    "technology": {
        "Senior Developer": Position(
            name="Senior Developer",
            level=PositionLevel.SENIOR,
            description="高级开发工程师",
            required_skills=["programming", "system_design", "mentoring"],
            max_agents=5
        ),
        "Junior Developer": Position(
            name="Junior Developer",
            level=PositionLevel.JUNIOR,
            description="初级开发工程师",
            required_skills=["programming", "testing"],
            max_agents=5
        ),
        "Tech Lead": Position(
            name="Tech Lead",
            level=PositionLevel.LEAD,
            description="技术负责人",
            required_skills=["programming", "system_design", "leadership"],
            max_agents=1
        ),
    },
    "data": {
        "Senior Analyst": Position(
            name="Senior Analyst",
            level=PositionLevel.SENIOR,
            description="高级数据分析师",
            required_skills=["data_analysis", "sql", "statistics", "visualization"],
            max_agents=3
        ),
        "Junior Analyst": Position(
            name="Junior Analyst",
            level=PositionLevel.JUNIOR,
            description="初级数据分析师",
            required_skills=["data_analysis", "sql"],
            max_agents=3
        ),
        "Data Lead": Position(
            name="Data Lead",
            level=PositionLevel.LEAD,
            description="数据负责人",
            required_skills=["data_analysis", "leadership", "strategy"],
            max_agents=1
        ),
    }
}

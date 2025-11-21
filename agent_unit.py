"""  
Agent Unit System
工作小组管理系统 - 动态组建项目小组
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import json


class UnitStatus(Enum):
    """Unit 状态"""
    FORMING = "forming"            # 组建中
    ACTIVE = "active"              # 活跃
    PAUSED = "paused"              # 暂停
    COMPLETED = "completed"        # 完成
    DISBANDED = "disbanded"        # 解散


class UnitRole(Enum):
    """Unit 中的角色"""
    LEAD = "lead"                  # 负责人/主导
    EXECUTOR = "executor"          # 执行者
    SUPPORTER = "supporter"        # 支持者


@dataclass
class UnitMember:
    """Unit 成员"""
    agent_id: str
    agent_name: str
    role: UnitRole                  # Unit 中的角色
    department_id: str              # 来自哪个部门
    position_name: str              # 原职位
    skills: List[str] = field(default_factory=list)
    responsibilities: str = ""      # 在 Unit 中的责任
    added_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": self.role.value,
            "department_id": self.department_id,
            "position_name": self.position_name,
            "skills": self.skills,
            "responsibilities": self.responsibilities,
            "added_at": self.added_at
        }


@dataclass
class AgentUnit:
    """工作小组"""
    id: str
    name: str
    description: str
    project_id: Optional[str] = None  # 关联的项目 ID
    
    lead_member: Optional[UnitMember] = None  # 小组负责人（必须存在）
    executor_members: List[UnitMember] = field(default_factory=list)  # 执行成员
    supporter_members: List[UnitMember] = field(default_factory=list)  # 支持成员
    
    status: UnitStatus = UnitStatus.FORMING
    priority: int = 0               # 优先级 (0-10)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    tasks: List[Dict[str, Any]] = field(default_factory=list)  # Unit 承接的任务
    
    def add_executor(self, member: UnitMember) -> bool:
        """添加执行成员"""
        if member.role != UnitRole.EXECUTOR:
            member.role = UnitRole.EXECUTOR
        self.executor_members.append(member)
        return True
    
    def add_supporter(self, member: UnitMember) -> bool:
        """添加支持成员"""
        if member.role != UnitRole.SUPPORTER:
            member.role = UnitRole.SUPPORTER
        self.supporter_members.append(member)
        return True
    
    def get_all_members(self) -> List[UnitMember]:
        """获取所有成员"""
        members = []
        if self.lead_member:
            members.append(self.lead_member)
        members.extend(self.executor_members)
        members.extend(self.supporter_members)
        return members
    
    def remove_member(self, agent_id: str) -> bool:
        """移除成员"""
        if self.lead_member and self.lead_member.agent_id == agent_id:
            # 不能移除负责人
            return False
        
        self.executor_members = [m for m in self.executor_members if m.agent_id != agent_id]
        self.supporter_members = [m for m in self.supporter_members if m.agent_id != agent_id]
        return True
    
    def activate(self) -> bool:
        """激活 Unit"""
        if self.status == UnitStatus.FORMING and self.lead_member:
            self.status = UnitStatus.ACTIVE
            self.started_at = datetime.now().isoformat()
            return True
        return False
    
    def pause(self) -> bool:
        """暂停 Unit"""
        if self.status == UnitStatus.ACTIVE:
            self.status = UnitStatus.PAUSED
            return True
        return False
    
    def resume(self) -> bool:
        """恢复 Unit"""
        if self.status == UnitStatus.PAUSED:
            self.status = UnitStatus.ACTIVE
            return True
        return False
    
    def complete(self) -> bool:
        """完成 Unit"""
        if self.status in [UnitStatus.ACTIVE, UnitStatus.PAUSED]:
            self.status = UnitStatus.COMPLETED
            self.completed_at = datetime.now().isoformat()
            return True
        return False
    
    def disband(self) -> bool:
        """解散 Unit"""
        self.status = UnitStatus.DISBANDED
        self.completed_at = datetime.now().isoformat()
        return True
    
    def assign_task(self, task: Dict[str, Any]) -> bool:
        """分配任务给 Unit"""
        self.tasks.append(task)
        return True
    
    def get_member_count(self) -> Dict[str, int]:
        """获取成员数量"""
        return {
            "lead": 1 if self.lead_member else 0,
            "executors": len(self.executor_members),
            "supporters": len(self.supporter_members),
            "total": len(self.get_all_members())
        }
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "lead_member": self.lead_member.to_dict() if self.lead_member else None,
            "executor_members": [m.to_dict() for m in self.executor_members],
            "supporter_members": [m.to_dict() for m in self.supporter_members],
            "status": self.status.value,
            "priority": self.priority,
            "member_count": self.get_member_count(),
            "tasks_count": len(self.tasks),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


class UnitManager:
    """Unit 管理器"""
    
    def __init__(self, storage_file: str = "/Users/viosson/units_config.json"):
        self.storage_file = storage_file
        self.units: Dict[str, AgentUnit] = {}
        self.load_units()
    
    def create_unit(
        self,
        unit_id: str,
        name: str,
        description: str,
        lead_member: UnitMember,
        project_id: Optional[str] = None,
        priority: int = 0
    ) -> Optional[AgentUnit]:
        """创建 Unit"""
        if unit_id in self.units:
            print(f"⚠️ Unit {unit_id} 已存在")
            return None
        
        unit = AgentUnit(
            id=unit_id,
            name=name,
            description=description,
            project_id=project_id,
            lead_member=lead_member,
            priority=priority
        )
        
        self.units[unit_id] = unit
        self.save_units()
        print(f"✓ Unit '{name}' 创建成功 (负责人: {lead_member.agent_name})")
        return unit
    
    def get_unit(self, unit_id: str) -> Optional[AgentUnit]:
        """获取 Unit"""
        return self.units.get(unit_id)
    
    def list_units(self) -> List[AgentUnit]:
        """列出所有 Unit"""
        return list(self.units.values())
    
    def list_units_by_status(self, status: UnitStatus) -> List[AgentUnit]:
        """按状态列出 Unit"""
        return [u for u in self.units.values() if u.status == status]
    
    def list_units_by_project(self, project_id: str) -> List[AgentUnit]:
        """按项目列出 Unit"""
        return [u for u in self.units.values() if u.project_id == project_id]
    
    def add_member_to_unit(
        self,
        unit_id: str,
        member: UnitMember,
        role: UnitRole
    ) -> bool:
        """添加成员到 Unit"""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        member.role = role
        
        if role == UnitRole.EXECUTOR:
            unit.add_executor(member)
        elif role == UnitRole.SUPPORTER:
            unit.add_supporter(member)
        
        self.save_units()
        print(f"✓ Agent '{member.agent_name}' 已添加到 Unit '{unit.name}' (角色: {role.value})")
        return True
    
    def remove_member_from_unit(self, unit_id: str, agent_id: str) -> bool:
        """从 Unit 移除成员"""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        result = unit.remove_member(agent_id)
        if result:
            self.save_units()
            print(f"✓ 成员已从 Unit '{unit.name}' 移除")
        return result
    
    def activate_unit(self, unit_id: str) -> bool:
        """激活 Unit"""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        result = unit.activate()
        if result:
            self.save_units()
            print(f"✓ Unit '{unit.name}' 已激活 (成员: {unit.get_member_count()['total']})")
        return result
    
    def complete_unit(self, unit_id: str) -> bool:
        """完成 Unit"""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        result = unit.complete()
        if result:
            self.save_units()
            print(f"✓ Unit '{unit.name}' 已完成")
        return result
    
    def disband_unit(self, unit_id: str) -> bool:
        """解散 Unit"""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        result = unit.disband()
        if result:
            self.save_units()
            print(f"✓ Unit '{unit.name}' 已解散")
        return result
    
    def assign_task_to_unit(
        self,
        unit_id: str,
        task_id: str,
        task_name: str,
        description: str = "",
        priority: int = 0
    ) -> bool:
        """分配任务给 Unit"""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        task = {
            "task_id": task_id,
            "task_name": task_name,
            "description": description,
            "priority": priority,
            "assigned_at": datetime.now().isoformat(),
            "status": "assigned"
        }
        
        unit.assign_task(task)
        self.save_units()
        print(f"✓ 任务 '{task_name}' 已分配给 Unit '{unit.name}'")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        active_units = [u for u in self.units.values() if u.status == UnitStatus.ACTIVE]
        completed_units = [u for u in self.units.values() if u.status == UnitStatus.COMPLETED]
        
        total_members = sum(len(u.get_all_members()) for u in self.units.values())
        total_tasks = sum(len(u.tasks) for u in self.units.values())
        
        return {
            "total_units": len(self.units),
            "active_units": len(active_units),
            "completed_units": len(completed_units),
            "total_members": total_members,
            "total_tasks": total_tasks,
            "units_by_status": {
                status.value: len([u for u in self.units.values() if u.status == status])
                for status in UnitStatus
            }
        }
    
    def search_units(
        self,
        name: Optional[str] = None,
        status: Optional[UnitStatus] = None,
        project_id: Optional[str] = None
    ) -> List[AgentUnit]:
        """搜索 Unit"""
        results = list(self.units.values())
        
        if name:
            results = [u for u in results if name.lower() in u.name.lower()]
        
        if status:
            results = [u for u in results if u.status == status]
        
        if project_id:
            results = [u for u in results if u.project_id == project_id]
        
        return results
    
    def save_units(self):
        """保存 Unit 配置"""
        data = {
            unit_id: unit.to_dict()
            for unit_id, unit in self.units.items()
        }
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存 Unit 配置失败: {e}")
    
    def load_units(self):
        """加载 Unit 配置"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for unit_id, unit_data in data.items():
                # 恢复负责人
                lead_data = unit_data.get("lead_member")
                lead_member = None
                if lead_data:
                    lead_member = UnitMember(
                        agent_id=lead_data["agent_id"],
                        agent_name=lead_data["agent_name"],
                        role=UnitRole(lead_data["role"]),
                        department_id=lead_data["department_id"],
                        position_name=lead_data["position_name"],
                        skills=lead_data["skills"],
                        responsibilities=lead_data["responsibilities"],
                        added_at=lead_data["added_at"]
                    )
                
                # 恢复成员
                executor_members = [
                    UnitMember(
                        agent_id=m["agent_id"],
                        agent_name=m["agent_name"],
                        role=UnitRole(m["role"]),
                        department_id=m["department_id"],
                        position_name=m["position_name"],
                        skills=m["skills"],
                        responsibilities=m["responsibilities"],
                        added_at=m["added_at"]
                    )
                    for m in unit_data.get("executor_members", [])
                ]
                
                supporter_members = [
                    UnitMember(
                        agent_id=m["agent_id"],
                        agent_name=m["agent_name"],
                        role=UnitRole(m["role"]),
                        department_id=m["department_id"],
                        position_name=m["position_name"],
                        skills=m["skills"],
                        responsibilities=m["responsibilities"],
                        added_at=m["added_at"]
                    )
                    for m in unit_data.get("supporter_members", [])
                ]
                
                unit = AgentUnit(
                    id=unit_data["id"],
                    name=unit_data["name"],
                    description=unit_data["description"],
                    project_id=unit_data.get("project_id"),
                    lead_member=lead_member,
                    executor_members=executor_members,
                    supporter_members=supporter_members,
                    status=UnitStatus(unit_data["status"]),
                    priority=unit_data.get("priority", 0),
                    created_at=unit_data["created_at"],
                    started_at=unit_data.get("started_at"),
                    completed_at=unit_data.get("completed_at")
                )
                
                self.units[unit_id] = unit
        
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ 加载 Unit 配置失败: {e}")

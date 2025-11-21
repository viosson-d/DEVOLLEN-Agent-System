"""  
Organization System Examples and Tests
组织系统示例和测试
"""

from organization_system import (
    OrganizationSystem, setup_default_organization,
    DepartmentType, PositionLevel
)

# 全局组织对象
_org = None

def get_org():
    """获取全局组织对象"""
    global _org
    if _org is None:
        _org = setup_default_organization()
    return _org


def example_1_setup_organization():
    """示例 1: 设置组织结构"""
    print("\n" + "="*60)
    print("【示例 1】设置组织结构")
    print("="*60)
    
    org = get_org()
    
    print("\n📋 部门列表:")
    depts = org.list_departments()
    for dept in depts:
        print(f"  • {dept['name']}")
        print(f"    - 类型: {dept['type']}")
        print(f"    - 负责人: {dept['lead']}")
        print(f"    - 职位: {', '.join(dept['positions'])}")


def example_2_add_agents():
    """示例 2: 添加 Agent 到部门"""
    print("\n" + "="*60)
    print("【示例 2】添加 Agent 到部门")
    print("="*60)
    
    org = get_org()
    
    # 添加 PM Agent
    print("\n添加 PM Agent:")
    org.add_agent_to_department(
        dept_id="pm_dept",
        agent_id="pm_001",
        agent_name="张三 - 项目经理",
        position_name="Senior PM",
        skills=["project_management", "leadership", "communication"]
    )
    
    org.add_agent_to_department(
        dept_id="pm_dept",
        agent_id="pm_002",
        agent_name="李四 - 项目经理",
        position_name="Senior PM",
        skills=["project_management", "risk_management", "communication"]
    )
    
    # 添加开发 Agent
    print("\n添加开发 Agent:")
    org.add_agent_to_department(
        dept_id="tech_dept",
        agent_id="dev_001",
        agent_name="王五 - 高级开发",
        position_name="Senior Developer",
        skills=["programming", "system_design", "python", "javascript"]
    )
    
    org.add_agent_to_department(
        dept_id="tech_dept",
        agent_id="dev_002",
        agent_name="赵六 - 初级开发",
        position_name="Junior Developer",
        skills=["programming", "testing", "python"]
    )
    
    # 添加数据 Agent
    print("\n添加数据分析 Agent:")
    org.add_agent_to_department(
        dept_id="data_dept",
        agent_id="analyst_001",
        agent_name="孙七 - 高级分析师",
        position_name="Senior Analyst",
        skills=["data_analysis", "sql", "statistics", "visualization"]
    )
    
    org.add_agent_to_department(
        dept_id="data_dept",
        agent_id="analyst_002",
        agent_name="周八 - 初级分析师",
        position_name="Junior Analyst",
        skills=["data_analysis", "sql"]
    )


def example_3_create_unit():
    """示例 3: 创建 Unit（工作小组）"""
    print("\n" + "="*60)
    print("【示例 3】创建 Unit（工作小组）")
    print("="*60)
    
    org = get_org()
    
    # 创建项目 A 的 Unit
    print("\n创建项目 A Unit:")
    unit_a = org.create_unit_from_agents(
        unit_id="unit_project_a",
        name="项目 A - 电商平台开发",
        description="负责新电商平台的开发和上线",
        lead_agent_id="pm_001",
        project_id="project_a",
        priority=9  # 高优先级
    )
    
    if unit_a:
        # 添加执行成员
        print("  添加执行成员:")
        org.add_executor_to_unit(
            unit_id="unit_project_a",
            agent_id="dev_001",
            responsibilities="核心开发，架构设计"
        )
        
        org.add_executor_to_unit(
            unit_id="unit_project_a",
            agent_id="analyst_001",
            responsibilities="性能分析，数据优化"
        )
        
        # 添加支持成员
        print("  添加支持成员:")
        org.add_supporter_to_unit(
            unit_id="unit_project_a",
            agent_id="dev_002",
            responsibilities="代码审查，测试支持"
        )
        
        # 激活 Unit
        print("  激活 Unit:")
        org.unit_manager.activate_unit("unit_project_a")
        
        # 显示 Unit 信息
        print("\n📋 Unit 详细信息:")
        unit_info = org.get_unit_info("unit_project_a")
        print(f"  名称: {unit_info['name']}")
        print(f"  状态: {unit_info['status']}")
        print(f"  优先级: {unit_info['priority']}/10")
        print(f"  负责人: {unit_info['lead']['agent_name']}")
        print(f"  执行成员:")
        for executor in unit_info['executors']:
            print(f"    - {executor['agent_name']} ({executor['position']})")
            print(f"      责任: {executor['responsibilities']}")
        print(f"  支持成员:")
        for supporter in unit_info['supporters']:
            print(f"    - {supporter['agent_name']} ({supporter['position']})")
            print(f"      责任: {supporter['responsibilities']}")


def example_4_find_agents():
    """示例 4: 查找合适的 Agent 加入 Unit"""
    print("\n" + "="*60)
    print("【示例 4】查找合适的 Agent 加入 Unit")
    print("="*60)
    
    org = get_org()
    
    # 查找具有特定技能的可用 Agent
    print("\n查找具有 'data_analysis' 技能的可用 Agent:")
    agents = org.find_agents_for_unit(
        skills=["data_analysis"],
        available_only=True
    )
    
    if agents:
        for agent in agents:
            print(f"  • {agent['agent_name']}")
            print(f"    - 部门: {agent['department']}")
            print(f"    - 职位: {agent['position']} ({agent['level']})")
            print(f"    - 技能: {', '.join(agent['skills'])}")
    else:
        print("  没有找到符合条件的 Agent")
    
    # 查找高级开发者
    print("\n查找高级开发者:")
    agents = org.find_agents_for_unit(
        position_level=PositionLevel.SENIOR,
        dept_type=DepartmentType.TECHNOLOGY
    )
    
    if agents:
        for agent in agents:
            print(f"  • {agent['agent_name']}")
            print(f"    - 职位: {agent['position']} ({agent['level']})")
    else:
        print("  没有找到符合条件的 Agent")


def example_5_agent_status():
    """示例 5: 查看 Agent 状态"""
    print("\n" + "="*60)
    print("【示例 5】查看 Agent 状态")
    print("="*60)
    
    org = get_org()
    
    print("\nAgent 'pm_001' 状态:")
    status = org.get_agent_status("pm_001")
    if status:
        print(f"  名称: {status['agent_name']}")
        print(f"  部门: {status['department']}")
        print(f"  职位: {status['position']} ({status['level']})")
        print(f"  技能: {', '.join(status['skills'])}")
        print(f"  可用: {status['availability']}")
        print(f"  所属 Unit: {status['assigned_unit_id']}")
    else:
        print("  Agent 不存在")


def example_6_organization_report():
    """示例 6: 生成组织状态报告"""
    print("\n" + "="*60)
    print("【示例 6】组织状态报告")
    print("="*60)
    
    org = get_org()
    
    # 生成并打印报告
    report = org.generate_report()
    print(report)


def example_7_release_agent():
    """示例 7: 从 Unit 释放 Agent"""
    print("\n" + "="*60)
    print("【示例 7】从 Unit 释放 Agent")
    print("="*60)
    
    org = get_org()
    
    print("\n当前 Agent 'dev_001' 状态:")
    status = org.get_agent_status("dev_001")
    if status:
        print(f"  可用: {status['availability']}")
        print(f"  所属 Unit: {status['assigned_unit_id']}")
    
    # 从 Unit 释放
    print("\n释放 Agent 'dev_001':")
    org.release_agent_from_unit("dev_001")
    
    print("\n释放后 Agent 'dev_001' 状态:")
    status = org.get_agent_status("dev_001")
    if status:
        print(f"  可用: {status['availability']}")
        print(f"  所属 Unit: {status['assigned_unit_id']}")


def example_8_disband_unit():
    """示例 8: 解散 Unit"""
    print("\n" + "="*60)
    print("【示例 8】解散 Unit 和释放成员")
    print("="*60)
    
    org = get_org()
    
    print("\n解散 Unit 'unit_project_a':")
    org.disband_unit("unit_project_a")
    
    print("\n检查成员状态:")
    for agent_id in ["pm_001", "dev_001", "analyst_001"]:
        status = org.get_agent_status(agent_id)
        if status:
            print(f"  {status['agent_name']}: 可用={status['availability']}, Unit={status['assigned_unit_id']}")


def main():
    """运行所有示例"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "组织系统演示 (Organization System Demo)" + " "*10 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # 设置组织结构
        example_1_setup_organization()
        
        # 添加 Agent
        example_2_add_agents()
        
        # 创建 Unit
        example_3_create_unit()
        
        # 查找 Agent
        example_4_find_agents()
        
        # 查看状态
        example_5_agent_status()
        
        # 组织报告
        example_6_organization_report()
        
        # 释放 Agent
        example_7_release_agent()
        
        # 解散 Unit
        example_8_disband_unit()
        
        print("\n" + "="*60)
        print("✅ 所有示例执行完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

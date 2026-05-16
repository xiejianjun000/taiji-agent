#!/usr/bin/env python3
"""代码质量检查"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print('=' * 80)
print('代码质量检查 - 导入测试')
print('=' * 80)

modules = [
    'taiji_agent.taiji_verify.delta_s',
    'taiji_agent.taiji_verify.kun_guard',
    'taiji_agent.taiji_verify.qian_advance',
    'taiji_agent.taiji_verify.fu_return',
    'taiji_agent.taiji_verify.xun_tune',
    'taiji_agent.taiji_verify.guan_observe',
    'taiji_agent.taiji_verify.polaris',
    'taiji_agent.taiji_verify.symptom_map',
    'taiji_agent.hermes_provider',
    'taiji_agent.hermes_engine',
    'taiji_agent.event_bus',
    'taiji_agent.plugin_system',
    'taiji_agent.sandbox',
    'taiji_agent.streaming',
    'taiji_agent.govmcp.crypto',
    'taiji_agent.govmcp.workflow',
    'taiji_agent.govmcp.tools',
    'taiji_agent.govmcp.plugins',
]

all_good = True
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except Exception as e:
        print(f'❌ {module}: {e}')
        all_good = False

print('=' * 80)
if all_good:
    print('所有模块导入成功！')
else:
    print('有模块导入失败！')
print('=' * 80)

sys.exit(0 if all_good else 1)

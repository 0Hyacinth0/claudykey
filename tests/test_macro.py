"""Macro 数据模型单元测试。"""
import pytest
from core.macro import Action, MacroSequence, TriggerConfig, MacroProject


class TestAction:
    """Action 类测试。"""
    
    def test_action_creation(self):
        """测试 Action 创建。"""
        action = Action(type='click', params={'x': 100, 'y': 200})
        assert action.type == 'click'
        assert action.params == {'x': 100, 'y': 200}
    
    def test_action_to_dict(self):
        """测试 Action 序列化。"""
        action = Action(type='key', params={'key': 'ctrl+c'})
        d = action.to_dict()
        assert d == {'type': 'key', 'params': {'key': 'ctrl+c'}}
    
    def test_action_from_dict(self):
        """测试 Action 反序列化。"""
        d = {'type': 'delay', 'params': {'ms': 1000}}
        action = Action.from_dict(d)
        assert action.type == 'delay'
        assert action.params == {'ms': 1000}
    
    def test_action_display_text_click(self):
        """测试点击动作显示文本。"""
        action = Action(type='click', params={'x': 100, 'y': 200})
        text = action.display_text()
        assert '点击' in text
        assert '100' in text
        assert '200' in text
    
    def test_action_display_text_delay(self):
        """测试延时动作显示文本。"""
        action = Action(type='delay', params={'ms': 500})
        text = action.display_text()
        assert '等待' in text
        assert '500' in text
    
    def test_action_display_text_loop_start(self):
        """测试循环开始动作显示文本。"""
        action = Action(type='loop_start', params={'count': 5})
        text = action.display_text()
        assert '开始循环' in text
        assert '5' in text
    
    def test_action_display_text_infinite_loop(self):
        """测试无限循环显示文本。"""
        action = Action(type='loop_start', params={'count': -1})
        text = action.display_text()
        assert '∞' in text or '无限' in text


class TestMacroSequence:
    """MacroSequence 类测试。"""
    
    def test_sequence_creation(self):
        """测试宏序列创建。"""
        seq = MacroSequence()
        assert seq.name == '新建宏'
        assert seq.actions == []
        assert seq.random_delay_min_ms == 50
        assert seq.random_delay_max_ms == 200
    
    def test_sequence_with_actions(self):
        """测试带动作的宏序列。"""
        seq = MacroSequence(name='测试宏')
        seq.actions.append(Action(type='click', params={'x': 0, 'y': 0}))
        seq.actions.append(Action(type='delay', params={'ms': 100}))
        
        assert len(seq.actions) == 2
        assert seq.actions[0].type == 'click'
        assert seq.actions[1].type == 'delay'
    
    def test_sequence_to_dict(self):
        """测试宏序列序列化。"""
        seq = MacroSequence(id='test123', name='测试宏')
        seq.actions.append(Action(type='click', params={'x': 10, 'y': 20}))
        
        d = seq.to_dict()
        assert d['id'] == 'test123'
        assert d['name'] == '测试宏'
        assert len(d['actions']) == 1
    
    def test_sequence_from_dict(self):
        """测试宏序列反序列化。"""
        d = {
            'id': 'abc123',
            'name': '导入的宏',
            'actions': [
                {'type': 'key', 'params': {'key': 'enter'}},
                {'type': 'delay', 'params': {'ms': 200}}
            ],
            'random_delay_min_ms': 100,
            'random_delay_max_ms': 300
        }
        
        seq = MacroSequence.from_dict(d)
        assert seq.id == 'abc123'
        assert seq.name == '导入的宏'
        assert len(seq.actions) == 2
        assert seq.random_delay_min_ms == 100
        assert seq.random_delay_max_ms == 300


class TestTriggerConfig:
    """TriggerConfig 类测试。"""
    
    def test_trigger_creation(self):
        """测试触发器创建。"""
        trigger = TriggerConfig()
        assert trigger.name == '新建触发器'
        assert trigger.enabled is True
        assert trigger.type == 'image'
    
    def test_image_trigger(self):
        """测试图像触发器。"""
        trigger = TriggerConfig(
            name='图像触发',
            type='image',
            template_path='/path/to/template.png',
            threshold=0.85
        )
        
        assert trigger.type == 'image'
        assert trigger.threshold == 0.85
    
    def test_text_trigger(self):
        """测试文字触发器。"""
        trigger = TriggerConfig(
            name='文字触发',
            type='text',
            target_text='开始',
            match_mode='contains'
        )
        
        assert trigger.type == 'text'
        assert trigger.target_text == '开始'
        assert trigger.match_mode == 'contains'
    
    def test_trigger_to_dict(self):
        """测试触发器序列化。"""
        trigger = TriggerConfig(
            id='trig001',
            name='测试触发器',
            type='image',
            region=(100, 100, 200, 150)
        )
        
        d = trigger.to_dict()
        assert d['id'] == 'trig001'
        assert d['name'] == '测试触发器'
        assert d['region'] == [100, 100, 200, 150]
    
    def test_trigger_from_dict(self):
        """测试触发器反序列化。"""
        d = {
            'id': 'trig002',
            'name': '导入的触发器',
            'enabled': False,
            'type': 'text',
            'region': [0, 0, 300, 200],
            'target_text': '完成',
            'match_mode': 'exact'
        }
        
        trigger = TriggerConfig.from_dict(d)
        assert trigger.id == 'trig002'
        assert trigger.enabled is False
        assert trigger.target_text == '完成'


class TestMacroProject:
    """MacroProject 类测试。"""
    
    def test_project_creation(self):
        """测试项目创建。"""
        project = MacroProject()
        assert project.macros == []
        assert project.triggers == []
        assert project.hotkey == '<f9>'
        assert project.mode == 'loop'
    
    def test_project_with_macros(self):
        """测试带宏的项目。"""
        project = MacroProject()
        project.macros.append(MacroSequence(name='宏1'))
        project.macros.append(MacroSequence(name='宏2'))
        
        assert len(project.macros) == 2
    
    def test_project_to_dict(self):
        """测试项目序列化。"""
        project = MacroProject()
        project.macros.append(MacroSequence(name='测试宏'))
        project.triggers.append(TriggerConfig(name='测试触发器'))
        
        d = project.to_dict()
        assert 'macros' in d
        assert 'triggers' in d
        assert len(d['macros']) == 1
        assert len(d['triggers']) == 1
    
    def test_project_from_dict(self):
        """测试项目反序列化。"""
        d = {
            'macros': [
                {'id': 'm1', 'name': '宏1', 'actions': []}
            ],
            'triggers': [
                {'id': 't1', 'name': '触发器1', 'type': 'image'}
            ],
            'hotkey': '<f10>',
            'mode': 'conditional',
            'input_backend': 'interception'
        }
        
        project = MacroProject.from_dict(d)
        assert len(project.macros) == 1
        assert len(project.triggers) == 1
        assert project.hotkey == '<f10>'
        assert project.mode == 'conditional'
        assert project.input_backend == 'interception'

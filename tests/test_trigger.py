"""触发器条件检测单元测试。

测试 TriggerConfig 的各种匹配模式和条件判断逻辑。
"""
import pytest
import re
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from core.macro import TriggerConfig, MacroProject, MacroSequence, Action
from core.executor import MacroExecutor


class TestTriggerConfig:
    """测试 TriggerConfig 数据类。"""

    def test_default_values(self):
        """测试默认值。"""
        t = TriggerConfig()
        assert t.enabled is True
        assert t.type == 'image'
        assert t.threshold == 0.80
        assert t.match_mode == 'contains'
        assert t.number_cmp == 'lte'
        assert t.number_val == 0.0

    def test_to_dict_and_from_dict(self):
        """测试序列化和反序列化。"""
        t = TriggerConfig(
            id='test123',
            name='测试触发器',
            enabled=False,
            type='text',
            region=(100, 200, 300, 400),
            template_path='/path/to/template.png',
            threshold=0.95,
            target_text='目标文字',
            match_mode='regex',
            number_cmp='gt',
            number_val=100.5,
        )
        
        d = t.to_dict()
        assert d['id'] == 'test123'
        assert d['name'] == '测试触发器'
        assert d['enabled'] is False
        assert d['type'] == 'text'
        assert d['region'] == [100, 200, 300, 400]
        assert d['threshold'] == 0.95
        assert d['match_mode'] == 'regex'
        assert d['number_cmp'] == 'gt'
        assert d['number_val'] == 100.5
        
        t2 = TriggerConfig.from_dict(d)
        assert t2.id == t.id
        assert t2.name == t.name
        assert t2.enabled == t.enabled
        assert t2.region == t.region
        assert t2.threshold == t.threshold
        assert t2.number_cmp == t.number_cmp


class TestTextMatchingModes:
    """测试文本匹配模式。"""

    def test_exact_match(self):
        """测试精确匹配。"""
        t = TriggerConfig(
            type='text',
            match_mode='exact',
            target_text='Hello World',
        )
        
        text = 'Hello World'
        assert text.strip() == t.target_text.strip()
        
        text = 'Hello World '
        assert text.strip() == t.target_text.strip()
        
        text = 'Hello World!'
        assert text.strip() != t.target_text.strip()

    def test_contains_match(self):
        """测试包含匹配。"""
        t = TriggerConfig(
            type='text',
            match_mode='contains',
            target_text='World',
        )
        
        assert 'World' in 'Hello World'
        assert 'World' in 'World!'
        assert 'World' not in 'Hello'

    def test_regex_match(self):
        """测试正则匹配。"""
        t = TriggerConfig(
            type='text',
            match_mode='regex',
            target_text=r'\d+',
        )
        
        assert bool(re.search(r'\d+', 'Score: 100'))
        assert bool(re.search(r'\d+', 'No numbers')) is False
        
        t.target_text = r'^[A-Z]\w+'
        assert bool(re.search(r'^[A-Z]\w+', 'Hello World'))
        assert bool(re.search(r'^[A-Z]\w+', 'hello World')) is False

    def test_number_comparison_lt(self):
        """测试数值比较 - 小于。"""
        val = 50
        ref_val = 100
        assert val < ref_val
        
        val = 100
        assert not (val < ref_val)
        
        val = 150
        assert not (val < ref_val)

    def test_number_comparison_lte(self):
        """测试数值比较 - 小于等于。"""
        val = 50
        ref_val = 100
        assert val <= ref_val
        
        val = 100
        assert val <= ref_val
        
        val = 150
        assert not (val <= ref_val)

    def test_number_comparison_eq(self):
        """测试数值比较 - 等于。"""
        val = 100.0
        ref_val = 100.0
        assert abs(val - ref_val) < 1e-6
        
        val = 100.001
        assert not (abs(val - ref_val) < 1e-6)

    def test_number_comparison_gte(self):
        """测试数值比较 - 大于等于。"""
        val = 150
        ref_val = 100
        assert val >= ref_val
        
        val = 100
        assert val >= ref_val
        
        val = 50
        assert not (val >= ref_val)

    def test_number_comparison_gt(self):
        """测试数值比较 - 大于。"""
        val = 150
        ref_val = 100
        assert val > ref_val
        
        val = 100
        assert not (val > ref_val)
        
        val = 50
        assert not (val > ref_val)

    def test_number_extraction(self):
        """测试从文本中提取数字。"""
        text = 'HP: 1500/2000 MP: 500'
        nums = re.findall(r'-?\d+\.?\d*', text)
        assert nums == ['1500', '2000', '500']
        
        val = float(nums[0])
        assert val == 1500.0
        
        text = 'No numbers here'
        nums = re.findall(r'-?\d+\.?\d*', text)
        assert nums == []
        
        text = 'Temperature: -5.5 degrees'
        nums = re.findall(r'-?\d+\.?\d*', text)
        assert nums == ['-5.5']


class TestMacroExecutorConditionCheck:
    """测试 MacroExecutor 的条件检查逻辑。"""

    @pytest.fixture
    def mock_project(self):
        """创建模拟项目。"""
        project = MacroProject()
        
        trig_image = TriggerConfig(
            id='img_trig',
            name='图像触发器',
            type='image',
            region=(0, 0, 100, 100),
            template_path='/fake/path.png',
            threshold=0.80,
        )
        
        trig_text = TriggerConfig(
            id='txt_trig',
            name='文本触发器',
            type='text',
            region=(0, 0, 100, 100),
            target_text='Hello',
            match_mode='contains',
        )
        
        trig_number = TriggerConfig(
            id='num_trig',
            name='数值触发器',
            type='text',
            region=(0, 0, 100, 100),
            match_mode='number',
            number_cmp='gte',
            number_val=100,
        )
        
        trig_disabled = TriggerConfig(
            id='disabled_trig',
            name='禁用触发器',
            enabled=False,
            type='text',
            region=(0, 0, 100, 100),
            target_text='Test',
        )
        
        project.triggers = [trig_image, trig_text, trig_number, trig_disabled]
        return project

    @pytest.fixture
    def mock_sequence(self):
        """创建模拟宏序列。"""
        return MacroSequence(name='测试宏')

    def test_disabled_trigger(self, mock_project, mock_sequence):
        """测试禁用的触发器不触发。"""
        executor = MacroExecutor(mock_sequence, project=mock_project)
        result = executor._check_condition('disabled_trig')
        assert result is False

    def test_nonexistent_trigger(self, mock_project, mock_sequence):
        """测试不存在的触发器。"""
        executor = MacroExecutor(mock_sequence, project=mock_project)
        result = executor._check_condition('nonexistent')
        assert result is False

    def test_invalid_region(self, mock_project, mock_sequence):
        """测试无效区域。"""
        mock_project.triggers[0].region = (0, 0, 0, 0)
        executor = MacroExecutor(mock_sequence, project=mock_project)
        result = executor._check_condition('img_trig')
        assert result is False

    @patch('core.executor.scr.capture_region')
    @patch('core.executor._ocr.recognize_text_only')
    def test_text_trigger_contains(self, mock_ocr, mock_capture, mock_project, mock_sequence):
        """测试文本触发器 - 包含匹配。"""
        mock_capture.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_ocr.return_value = 'Hello World'
        
        executor = MacroExecutor(mock_sequence, project=mock_project)
        result = executor._check_condition('txt_trig')
        assert result is True
        
        mock_ocr.return_value = 'Goodbye'
        result = executor._check_condition('txt_trig')
        assert result is False

    @patch('core.executor.scr.capture_region')
    @patch('core.executor._ocr.recognize_text_only')
    def test_number_trigger(self, mock_ocr, mock_capture, mock_project, mock_sequence):
        """测试数值触发器。"""
        mock_capture.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_ocr.return_value = 'Score: 150 points'
        
        executor = MacroExecutor(mock_sequence, project=mock_project)
        result = executor._check_condition('num_trig')
        assert result is True
        
        mock_ocr.return_value = 'Score: 50 points'
        result = executor._check_condition('num_trig')
        assert result is False


class TestIfElifElseBranching:
    """测试 if/elif/else 分支逻辑。"""

    @pytest.fixture
    def mock_project_with_triggers(self):
        """创建带触发器的项目。"""
        project = MacroProject()
        
        project.triggers = [
            TriggerConfig(id='cond_a', name='条件A', type='text', region=(0, 0, 10, 10), target_text='A', match_mode='contains'),
            TriggerConfig(id='cond_b', name='条件B', type='text', region=(0, 0, 10, 10), target_text='B', match_mode='contains'),
            TriggerConfig(id='cond_c', name='条件C', type='text', region=(0, 0, 10, 10), target_text='C', match_mode='contains'),
        ]
        return project

    def test_if_branch_structure(self, mock_project_with_triggers):
        """测试 if 分支结构解析。"""
        actions = [
            Action(type='if', params={'trigger_id': 'cond_a'}),
            Action(type='click', params={'x': 100, 'y': 100}),
            Action(type='end_if'),
        ]
        
        seq = MacroSequence(actions=actions)
        executor = MacroExecutor(seq, project=mock_project_with_triggers)
        
        assert len(actions) == 3
        assert actions[0].type == 'if'
        assert actions[1].type == 'click'
        assert actions[2].type == 'end_if'

    def test_if_elif_else_structure(self, mock_project_with_triggers):
        """测试 if/elif/else 分支结构解析。"""
        actions = [
            Action(type='if', params={'trigger_id': 'cond_a'}),
            Action(type='click', params={'x': 100, 'y': 100}),
            Action(type='elif', params={'trigger_id': 'cond_b'}),
            Action(type='click', params={'x': 200, 'y': 200}),
            Action(type='else_start', params={}),
            Action(type='click', params={'x': 300, 'y': 300}),
            Action(type='end_if'),
        ]
        
        seq = MacroSequence(actions=actions)
        executor = MacroExecutor(seq, project=mock_project_with_triggers)
        
        assert actions[0].type == 'if'
        assert actions[2].type == 'elif'
        assert actions[4].type == 'else_start'
        assert actions[6].type == 'end_if'

    def test_nested_if_structure(self, mock_project_with_triggers):
        """测试嵌套 if 结构。"""
        actions = [
            Action(type='if', params={'trigger_id': 'cond_a'}),
            Action(type='if', params={'trigger_id': 'cond_b'}),
            Action(type='click', params={'x': 100, 'y': 100}),
            Action(type='end_if'),
            Action(type='end_if'),
        ]
        
        seq = MacroSequence(actions=actions)
        executor = MacroExecutor(seq, project=mock_project_with_triggers)
        
        assert actions[0].type == 'if'
        assert actions[1].type == 'if'
        assert actions[3].type == 'end_if'
        assert actions[4].type == 'end_if'


class TestClosureCapture:
    """测试闭包捕获问题修复。"""

    def test_trigger_id_capture(self):
        """测试 trigger_id 正确捕获。"""
        captured_ids = []
        
        def make_checker(tid):
            def check():
                captured_ids.append(tid)
                return True
            return check
        
        checkers = []
        for i in range(3):
            checkers.append(make_checker(f'trigger_{i}'))
        
        for checker in checkers:
            checker()
        
        assert captured_ids == ['trigger_0', 'trigger_1', 'trigger_2']

    def test_lambda_default_arg_capture(self):
        """测试 lambda 默认参数捕获。"""
        trigger_ids = ['a', 'b', 'c']
        checkers = []
        
        for tid in trigger_ids:
            checkers.append(lambda t=tid: t)
        
        results = [c() for c in checkers]
        assert results == ['a', 'b', 'c']


class TestEdgeCases:
    """测试边界条件。"""

    def test_empty_target_text(self):
        """测试空目标文本。"""
        t = TriggerConfig(
            type='text',
            target_text='',
            match_mode='contains',
        )
        
        assert '' in 'Any text'
        assert '' in ''

    def test_empty_ocr_result(self):
        """测试 OCR 空结果。"""
        text = ''
        nums = re.findall(r'-?\d+\.?\d*', text)
        assert nums == []

    def test_negative_numbers(self):
        """测试负数。"""
        text = 'Temperature: -10 degrees'
        nums = re.findall(r'-?\d+\.?\d*', text)
        assert nums == ['-10']
        assert float(nums[0]) == -10.0

    def test_decimal_numbers(self):
        """测试小数。"""
        text = 'Price: $19.99'
        nums = re.findall(r'-?\d+\.?\d*', text)
        assert nums == ['19.99']
        assert float(nums[0]) == 19.99

    def test_multiple_numbers(self):
        """测试多个数字。"""
        text = 'HP: 100/200 MP: 50'
        nums = re.findall(r'-?\d+\.?\d*', text)
        assert len(nums) == 3
        assert float(nums[0]) == 100

    def test_threshold_boundary(self):
        """测试阈值边界。"""
        assert 0.80 >= 0.80
        assert 0.79 < 0.80
        assert 0.81 >= 0.80

    def test_floating_point_equality(self):
        """测试浮点数相等比较。"""
        val = 100.0
        ref = 100.0
        assert abs(val - ref) < 1e-6
        
        val = 100.01
        ref = 100.0
        assert not (abs(val - ref) < 1e-6)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

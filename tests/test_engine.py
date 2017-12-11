from unittest.mock import Mock

from .utils import TestCANToolz


class TestEngine(TestCANToolz):

    def test_start_loop(self):
        mock_module = Mock()
        self.CANEngine._actions = [['mock_module', mock_module, {'pipe': 42}]]
        self.CANEngine.start_loop()
        mock_module.do_start.assert_called_once()

    def test_start_loop_several(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        self.CANEngine.start_loop()
        for mock_module in mock_modules:
            mock_module.do_start.assert_called_once()

    def test_call_module_valid_id(self):
        mock_module = Mock()
        self.CANEngine._actions = [['mock_module', mock_module, {'pipe': 42}]]
        self.CANEngine.call_module(0, 'mock call')
        mock_module.raw_write.assert_called_once_with('mock call')

    def test_call_module_valid_id_several(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        self.CANEngine.call_module(5, 'mock call')
        for i, mock_module in enumerate(mock_modules):
            if i == 5:
                mock_module.raw_write.assert_called_once_with('mock call')
            else:
                mock_module.raw_write.assert_not_called()

    def test_call_module_invalid_id(self):
        mock_module = Mock()
        self.CANEngine._actions = [['mock_module', mock_module, {'pipe': 42}]]
        res = self.CANEngine.call_module(-1, 'mock call')
        mock_module.raw_write.assert_not_called()
        self.assertTrue(res == 'Module -1 not found!')

    def test_call_module_invalid_id_several(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        res = self.CANEngine.call_module(10, 'mock call')
        for mock_module in mock_modules:
            mock_module.raw_write.assert_not_called()
        self.assertTrue(res == 'Module 10 not found!')

    def test_find_module(self):
        mock_module = Mock()
        self.CANEngine._actions = [['mock_module', mock_module, {'pipe': 42}]]
        index = self.CANEngine.find_module('mock_module')
        self.assertTrue(index == 0)

    def test_find_module_several(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        for i in range(10):
            index = self.CANEngine.find_module('mock_module%d' % i)
            self.assertTrue(index == i)

    def test_find_module_invalid(self):
        index = self.CANEngine.find_module('mock_module')
        self.assertTrue(index == -1)

    def test_find_module_several_invalid(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        index = self.CANEngine.find_module('mock_module11')
        self.assertTrue(index == -1)

    def test_edit_module(self):
        mock_module = Mock()
        self.CANEngine._actions = [['mock_module', mock_module, {'pipe': 42}]]
        res = self.CANEngine.edit_module(0, {'pipe': 13})
        self.assertTrue(res)
        self.assertTrue(self.CANEngine._actions[0][2] == {'pipe': 13})

    def test_edit_module_several(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        for i in range(10):
            res = self.CANEngine.edit_module(i, {'pipe': 13})
            self.assertTrue(res)
            self.assertTrue(self.CANEngine._actions[i][2] == {'pipe': 13})

    def test_edit_module_invalid(self):
        res = self.CANEngine.edit_module(-1, {'pipe': 42})
        self.assertFalse(res)

    def test_edit_module_several_invalid(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        for i in range(10):
            res = self.CANEngine.edit_module(i + 10, {'pipe': 13})
            self.assertFalse(res)
            self.assertTrue(self.CANEngine._actions[i][2] == {'pipe': 42})

    def test_attribute_actions(self):
        self.CANEngine._actions = [[1, 2, 3]]
        actions = self.CANEngine.actions
        self.assertTrue(actions == [[1, 2, 3]])

    def test_attribute_modules(self):
        self.CANEngine._modules = {'mock_module': 42}
        modules = self.CANEngine.modules
        self.assertTrue(modules == {'mock_module': 42})

    def test_engine_exit(self):
        mock_module = Mock()
        self.CANEngine._actions = [['mock_module', mock_module, {'pipe': 42}]]
        self.CANEngine.engine_exit()
        mock_module.do_exit.assert_called_once()

    def test_engine_exit_several(self):
        mock_modules = [Mock() for _ in range(10)]
        self.CANEngine._actions = [['mock_module%d' % i, mock_module, {'pipe': 42}] for i, mock_module in enumerate(mock_modules)]
        self.CANEngine.engine_exit()
        for mock_module in mock_modules:
            mock_module.do_exit.assert_called_once()

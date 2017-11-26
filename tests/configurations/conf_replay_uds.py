# Test scenario/configuration
modules = {
    'ping': {'bus': 'Default'},
    'analyze': {'debug': 2},
    'replay': {'load_from': 'tests/data/test_responses.save', 'debug': 2, 'bus': 'Default'}
}
# The test scenario logic
actions = [
    {'replay': {'pipe': 1}},
    {'analyze': {'pipe': 1}},
    {'ping': {
        'pipe': 2,
        'range': [1790, 1810],
        'services':[
            {'service': 0x01, 'sub': 0x0d},
            {'service': 0x09, 'sub': 0x02},
            {'service': 0x2F, 'sub': 0x03, 'data': [7, 3, 0, 0]}],
        'mode':'UDS'}},
    {'analyze': {'pipe': 2}}]

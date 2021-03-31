import config.config_sys as cfg_sys

__serviceSet = {
    'service01': {'size': 2, 'cost': 0.2, 'speed': [50, 100], 'miu': 100},
    'service02': {'size': 5, 'cost': 0.3, 'speed': [10, 20], 'miu': 50},
    'service03': {'size': 5, 'cost': 0.5, 'speed': [20, 40], 'miu': 85},
    'service04': {'size': 5, 'cost': 0.7, 'speed': [45, 70], 'miu': 70},
    'service05': {'size': 5, 'cost': 0.1, 'speed': [15, 25], 'miu': 77},
    'service06': {'size': 5, 'cost': 0.4, 'speed': [17, 26], 'miu': 45},
    'service07': {'size': 5, 'cost': 0.6, 'speed': [62, 80], 'miu': 66},
    'service08': {'size': 5, 'cost': 0.8, 'speed': [99, 99], 'miu': 32},
    'service09': {'size': 5, 'cost': 1.1, 'speed': [10, 10], 'miu': 100},
    'service10': {'size': 5, 'cost': 0.4, 'speed': [12, 25], 'miu': 150},
}
__nodeSet = {
    '134.122.119.166':
        {'alias': 'cl01', 'price': 0.1, 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 5},
    '143.198.64.134':
        {'alias': 'cl02', 'price': 0.2, 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 7},
    '143.198.219.100':
        {'alias': 'dc01', 'price': 0.3, 'typee': cfg_sys.TYPEE_DC, 'capacity': cfg_sys.MAX},
}
__edgeList = [
    {'src': 'dc01', 'dst': 'cl01', 'price': 0.01, 'priceReverse': 0.02},
    {'src': 'dc01', 'dst': 'cl02', 'price': 0.01, 'priceReverse': 0.02},
    {'src': 'cl01', 'dst': 'cl02', 'price': 0.005, 'priceReverse': 0.005},
]

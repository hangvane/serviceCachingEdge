import config.config_sys as cfg_sys

__serviceSet = {
    'service01': {'cost': 0, 'speed': [50, 100], 'size': 2 * 0, 'miu': 200},
    'service02': {'cost': 0, 'speed': [62, 80], 'size': 8 * 0, 'miu': 450},
    'service03': {'cost': 0, 'speed': [90, 100], 'size': 8 * 0, 'miu': 250},
    'service04': {'cost': 0, 'speed': [20, 20], 'size': 13 * 0, 'miu': 700},
    'service05': {'cost': 0, 'speed': [24, 50], 'size': 6 * 0, 'miu': 800},
}

__distanceMat = {
    'SV_': {'SV_': 0, 'SYD': 12000, 'SGP': 13632, 'VA_': 4040, 'FRA': 9149, 'LON': 8632},
    'SYD': {'SV_': 12000, 'SYD': 0, 'SGP': 6277, 'VA_': 15785, 'FRA': 16464, 'LON': 16971},
    'SGP': {'SV_': 13632, 'SYD': 6277, 'SGP': 0, 'VA_': 15776, 'FRA': 10265, 'LON': 10850},
    'VA_': {'SV_': 4040, 'SYD': 15785, 'SGP': 15776, 'VA_': 0, 'FRA': 6615, 'LON': 5985},
    'FRA': {'SV_': 9149, 'SYD': 16464, 'SGP': 10265, 'VA_': 6615, 'FRA': 0, 'LON': 632},
    'LON': {'SV_': 8632, 'SYD': 16971, 'SGP': 10850, 'VA_': 5985, 'FRA': 632, 'LON': 0},
}

__nodeSet = {
    '47.254.40.176': {'alias': 'cl01_1_SV_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.74.70.166': {'alias': 'cl02_1_SYD', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.241.117.38': {'alias': 'cl03_1_SGP', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.89.153.189': {'alias': 'cl04_1_VA_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '8.209.101.179': {'alias': 'cl05_1_FRA', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.251.5.3': {'alias': 'cl06_2_SV_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.74.66.47': {'alias': 'cl07_2_SYD', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '8.208.114.205': {'alias': 'cl08_1_LON', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.90.254.132': {'alias': 'cl09_2_VA_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.91.89.23': {'alias': 'cl10_2_FRA', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.251.10.102': {'alias': 'cl11_3_SV_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.74.69.226': {'alias': 'cl12_3_SYD', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '8.208.114.201': {'alias': 'cl13_2_LON', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.241.162.152': {'alias': 'cl14_2_SGP', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '8.209.103.219': {'alias': 'cl15_3_FRA', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '198.11.179.212': {'alias': 'cl16_4_SV_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.91.40.87': {'alias': 'cl17_4_SYD', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.241.160.123': {'alias': 'cl18_3_SGP', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.89.152.144': {'alias': 'cl19_3_VA_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '8.209.89.117': {'alias': 'cl20_4_FRA', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.251.13.39': {'alias': 'cl21_5_SV_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.74.70.71': {'alias': 'cl22_5_SYD', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '8.208.86.185': {'alias': 'cl23_3_LON', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.252.28.116': {'alias': 'cl24_4_VA_', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '8.209.101.73': {'alias': 'cl25_5_FRA', 'typee': cfg_sys.TYPEE_CL_USER, 'capacity': 1, 'price': cfg_sys.PRICE_CL},
    '47.88.0.69': {'alias': 'dc01_1_SV_', 'typee': cfg_sys.TYPEE_DC, 'capacity': cfg_sys.MAX},
    '47.91.45.177': {'alias': 'dc02_1_SYD', 'typee': cfg_sys.TYPEE_DC, 'capacity': cfg_sys.MAX},
    '8.208.90.82': {'alias': 'dc03_1_LON', 'typee': cfg_sys.TYPEE_DC, 'capacity': cfg_sys.MAX},
    '47.241.168.144': {'alias': 'dc04_1_SGP', 'typee': cfg_sys.TYPEE_DC, 'capacity': cfg_sys.MAX},
    '47.252.19.79': {'alias': 'dc05_1_VA_', 'typee': cfg_sys.TYPEE_DC, 'capacity': cfg_sys.MAX},
}

__edgeList = [
    {'src': 'dc02_1_SYD', 'dst': 'dc04_1_SGP', 'price': 2.21e-3, 'priceReverse': 3.53e-3},
    {'src': 'dc02_1_SYD', 'dst': 'dc03_1_LON', 'price': 2.47e-3, 'priceReverse': 2.79e-3},
    {'src': 'dc02_1_SYD', 'dst': 'dc01_1_SV_', 'price': 4.92e-3, 'priceReverse': 2.25e-3},
    {'src': 'dc04_1_SGP', 'dst': 'dc01_1_SV_', 'price': 2.26e-3, 'priceReverse': 4.66e-3},
    {'src': 'dc03_1_LON', 'dst': 'dc01_1_SV_', 'price': 4.60e-3, 'priceReverse': 4.11e-3},
    {'src': 'dc03_1_LON', 'dst': 'dc05_1_VA_', 'price': 2.32e-3, 'priceReverse': 2.34e-3},
    {'src': 'dc05_1_VA_', 'dst': 'dc01_1_SV_', 'price': 4.15e-3, 'priceReverse': 2.08e-3},
    {'src': 'dc01_1_SV_', 'dst': 'cl01_1_SV_', 'price': 4.17e-3, 'priceReverse': 2.66e-3},
    {'src': 'dc02_1_SYD', 'dst': 'cl02_1_SYD', 'price': 4.12e-3, 'priceReverse': 2.36e-3},
    {'src': 'dc04_1_SGP', 'dst': 'cl03_1_SGP', 'price': 4.06e-3, 'priceReverse': 4.82e-3},
    {'src': 'dc05_1_VA_', 'dst': 'cl04_1_VA_', 'price': 4.31e-3, 'priceReverse': 4.19e-3},
    {'src': 'dc03_1_LON', 'dst': 'cl05_1_FRA', 'price': 4.47e-3, 'priceReverse': 3.33e-3},
    {'src': 'cl01_1_SV_', 'dst': 'cl06_2_SV_', 'price': 4.72e-3, 'priceReverse': 3.72e-3},
    {'src': 'cl02_1_SYD', 'dst': 'cl07_2_SYD', 'price': 2.62e-3, 'priceReverse': 2.74e-3},
    {'src': 'dc03_1_LON', 'dst': 'cl08_1_LON', 'price': 3.90e-3, 'priceReverse': 3.48e-3},
    {'src': 'cl04_1_VA_', 'dst': 'cl09_2_VA_', 'price': 2.76e-3, 'priceReverse': 3.74e-3},
    {'src': 'cl05_1_FRA', 'dst': 'cl10_2_FRA', 'price': 2.40e-3, 'priceReverse': 3.20e-3},
    {'src': 'cl01_1_SV_', 'dst': 'cl11_3_SV_', 'price': 2.89e-3, 'priceReverse': 2.00e-3},
    {'src': 'cl02_1_SYD', 'dst': 'cl12_3_SYD', 'price': 2.64e-3, 'priceReverse': 2.02e-3},
    {'src': 'cl08_1_LON', 'dst': 'cl13_2_LON', 'price': 3.72e-3, 'priceReverse': 4.31e-3},
    {'src': 'cl03_1_SGP', 'dst': 'cl14_2_SGP', 'price': 2.24e-3, 'priceReverse': 4.16e-3},
    {'src': 'cl05_1_FRA', 'dst': 'cl15_3_FRA', 'price': 2.66e-3, 'priceReverse': 4.83e-3},
    {'src': 'cl01_1_SV_', 'dst': 'cl16_4_SV_', 'price': 2.27e-3, 'priceReverse': 4.69e-3},
    {'src': 'cl02_1_SYD', 'dst': 'cl17_4_SYD', 'price': 4.60e-3, 'priceReverse': 2.28e-3},
    {'src': 'cl03_1_SGP', 'dst': 'cl18_3_SGP', 'price': 2.63e-3, 'priceReverse': 3.60e-3},
    {'src': 'cl04_1_VA_', 'dst': 'cl19_3_VA_', 'price': 4.65e-3, 'priceReverse': 4.06e-3},
    {'src': 'cl05_1_FRA', 'dst': 'cl20_4_FRA', 'price': 4.45e-3, 'priceReverse': 4.23e-3},
    {'src': 'cl01_1_SV_', 'dst': 'cl21_5_SV_', 'price': 3.21e-3, 'priceReverse': 2.05e-3},
    {'src': 'cl02_1_SYD', 'dst': 'cl22_5_SYD', 'price': 3.72e-3, 'priceReverse': 4.39e-3},
    {'src': 'cl08_1_LON', 'dst': 'cl23_3_LON', 'price': 3.16e-3, 'priceReverse': 3.85e-3},
    {'src': 'cl04_1_VA_', 'dst': 'cl24_4_VA_', 'price': 4.79e-3, 'priceReverse': 2.53e-3},
    {'src': 'cl05_1_FRA', 'dst': 'cl25_5_FRA', 'price': 3.47e-3, 'priceReverse': 3.93e-3},
]

# triple price of links with DC
for i in range(len(__edgeList)):
    if __edgeList[i]['src'].startswith('dc') or __edgeList[i]['src'].startswith('dc'):
        __edgeList[i]['price'] *= cfg_sys.PRICE_LINK_DC_FACTOR
        __edgeList[i]['priceReverse'] *= cfg_sys.PRICE_LINK_DC_FACTOR
pass

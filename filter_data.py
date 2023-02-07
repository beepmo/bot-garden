import re
import time

all = 'All gardens'
_4c = 'Carolinian Forest'
_1c = 'Contemporary Garden'
_1p = 'Winter Garden'
alp = 'Alpine Garden'
_1b = 'BC Rainforest'
_dp = 'Dwarf Pinetum'
_1e = 'Old Entrance Garden'
_1g = 'Garry Oak Meadow & Woodland'
_1j = 'Pacific Slope Woodland'
_1m = 'Pavilion Beds'
_1r = 'Service Yard'
_1s = 'Lawn & Lake'
_1x = 'Service Berm, Perimeter'
_2a = 'Office Complex'
_3a = 'Asian Garden'
foo = 'Food Garden'
_fn = 'NE Fence'
_fs = 'SW Fence'
_1f = 'Physic Garden'
_rb = 'Arbour Garden'
_1d = 'Arbour'
# laa = 'Alpine Australasia'
# # laf = 'Alpine Africa'
# las = 'Alpine Asia'  # include 'LAM'
# lsa = 'Alpine South America'
# # lna = 'Alpine North America'
# lcs = 'Alpine Cactus and Succulent'  # include 'LTC'
# leu = 'Alpine Europe'


GARDENS = [all, _4c, _1p, alp, _1b, _dp, _1e, _1g, _1j, _1m, _1r, _1s, _1x, _2a, _3a,
           foo, _fn, _fs, _1f, _rb, _1d]


def build_pattern(gardens_set):
    regex = '^'

    if _4c in gardens_set:
        regex += '4C[0-1]\d|'
    if _1c in gardens_set:
        regex += '1C0[1-4]|'
    if _1p in gardens_set:
        regex += '1P0[1-6]|'
    if alp in gardens_set:
        regex += 'LAA[1-4]|LAF[1-2]|LAS[1-6]|LBF[1-3]|LAM|LSA[1-2]|LSA\d|LNA[1-6]|LCS[1-3]|LTC[1-2]|LEU[1-3]|LFE|'
    if _1b in gardens_set:
        regex += '1B[1-4]\d|'
    if _dp in gardens_set:
        regex += '1DP[1-2]|'
    if _1e in gardens_set:
        regex += '1E0[1-2]|'
    if _1g in gardens_set:
        regex += '1G0[1-5]|'
    if _1j in gardens_set:
        regex += '1J0[1-4]|'
    if _1m in gardens_set:
        regex += '1M0[1-9]|'
    if _1r in gardens_set:
        regex += '1R01|'
    if _1s in gardens_set:
        regex += '1S0[1-2]|'
    if _1x in gardens_set:
        regex += '1X0[1-2]|'
    if _2a in gardens_set:
        regex += '2A[0-1]\d|'
    if _3a in gardens_set:
        regex += '3A[A-W][A-Z0-9]|'
    if foo in gardens_set:
        regex += 'F|1K([0-2]\d|CF)|'  # accept garden component F, cold frame 1KCF
    if _fn in gardens_set:
        regex += 'FN0[1-2]|'
    if _fs in gardens_set:
        regex += 'FS0[1-6]|'
    if _1f in gardens_set:
        regex += '1F([0-1]\d|PL)|'  # accept planters 1FPL
    if _rb in gardens_set:
        regex += 'RB|'
    if _1d in gardens_set:
        regex += '1D|'
    # # if laf in gardens_set:
    # #     regex += 'LAF\d|'
    # if las in gardens_set:
    #     regex += 'LAS\d|LAM|'
    # if lsa in gardens_set:
    #     regex += 'LSA\d|'
    # # if lna in gardens_set:
    # #     regex += 'LNA\d'
    # if lcs in gardens_set:
    #     regex += 'LCS\d|LTC\d|'
    # if leu in gardens_set:
    #     regex += 'LEU\d|'

    regex += '$'
    return regex


def filter_bed(df, gardens_set):
    if all in gardens_set:
        return df

    filter_bed_start = time.time()

    bed_pattern = build_pattern(gardens_set)
    filtered = df[df.Bed.str.match(bed_pattern)]

    filter_bed_stop = time.time()

    print(
        f'Time taken to apply filter is {(filter_bed_stop - filter_bed_start)}. \n Gardens selected: {gardens_set}')

    return filtered

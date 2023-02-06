import time as tim
import pandas as pd

from request_csv import csv_pddf
from datetime import datetime

# -------------------------------------------------------
# Parse constants that control what data we display

# client-specified cutoff time before which data is less reliable
FUZZY = datetime.strptime('2016', '%Y')
delta_fuzzy = datetime.today() - FUZZY
FUZZY_AGE = delta_fuzzy.days

GENUS = ('',
         'Acer',
         'Magnolia',
         'Rhododendron',
         'Cornus',
         'Sorbus',
         'Clematis',
         )

ATTRIBUTES = ('Species Count', 'Item Count', 'Label Stats', 'Geo-record Stats')

# list of bed codes not on the map
EXCLUDED_PREFIXES = ['H',  # herbariums
                     '5',  # nitobe
                     '8',  # nursery
                     '9',  # unknown
                     ]


# -------------------------------------------------------
# Parsed dataframe column names

L_ONLY = 'Labelled, not geo-recorded'
G_ONLY = 'Geo-recorded, not labelled'
L_AND_G = 'Labelled and Geo-recorded'
NOT_L_NOR_G = 'Not labelled nor geo-recorded'
LGPF = 'Labelled, Geo-recorded, Post-Fuzzy'

ITEMS = 'Item Count'

# -------------------------------------------------------
# store for today, before new csv drops tomorrow
CACHE = []


# -------------------------------------------------------
# create one row of attributes for each bed


def make_df(genus):  # alltab_genus is string

    # -------------------------------------------------------
    # lists to build into df series

    # list of beds
    beds = []

    # per-bed data lists in which the ith entry corresponds to the ith bed in beds:

    # list of species lists
    species_in_bed = []

    # list of numbers
    items_in_bed = []
    l_total_percent = []
    g_total_percent = []

    '''# l = labelled
    # g = geo-recorded
    # r = reported after date
    # counts, not percentages'''
    lgr = []
    l = []
    g = []
    lg = []
    not_lg = []

    start = tim.time()

    # populate the lists bed and species_in_bed
    for index, row in csv_pddf.iterrows():  # iterate over all rows of data

        species = row['Taxon']

        if genus and (species.partition(' ')[0] != genus):
            continue

        bed = row['Bed']
        # just for this data source
        if bed == 'HUBC' or bed == 'HBG' or bed == 'HEXT':
            continue

        labelled = row['Label']
        georecorded = row['Geo?']
        age = row['Days Since Sighted']

        if bed in beds:
            # bed is in beds
            bed_location = beds.index(bed)

            # update item count
            items_in_bed[bed_location] += 1

            # update species
            in_this_bed = species_in_bed[bed_location]
            if not species in in_this_bed:
                in_this_bed.append(species)

            # affirmative action for item in known bed
            # for some reason this throws invalid syntax when lambda
            def increment_here(list):
                list[bed_location] += 1
                return

            try:
                process_item(increment_here, lambda list: None,
                             labelled, georecorded, age,
                             l_total_percent, g_total_percent, lg, lgr, not_lg, l, g)
            except IndexError:
                print(f'l: {len(l)}'
                      f'g: {len(g)}'
                      f'lg: {len(lg)}'
                      f'lgr: {len(lgr)}'
                      f'not_lg: {len(not_lg)}')
                return

            try:
                assert l_total_percent[bed_location] <= items_in_bed[bed_location]
            except AssertionError:
                print(f'l_total_percent:\n{l_total_percent}\n'
                      f'items:\n{items_in_bed}')
                return
        else:
            # bed is not in beds

            # add bed to beds
            beds.append(bed)

            # add species as list
            species_in_bed.append([species])

            # count item as list
            items_in_bed.append(1)

            try:
                # process_item(append_1, append_0, labelled, georecorded, age)
                process_item((lambda cur_list: cur_list.append(1)), (lambda cur_list: cur_list.append(0)),
                             labelled, georecorded, age,
                             l_total_percent, g_total_percent, lg, lgr, not_lg, l, g)
            except AttributeError:

                print(f'l: {type(l)}'
                      f'g: {type(g)}'
                      f'lg: {type(lg)}'
                      f'lgr: {type(lgr)}'
                      f'not_lg: {type(not_lg)}')
                return

    # -------------------------------------------------------
    # turn counts into plottable

    # species count by bed, in same order as beds
    species_cnts = []

    for j in range(len(beds)):
        # -------------------------------------------------------
        # get tag as int percentage
        if l_total_percent[j] > items_in_bed[j] * 1.2:
            print(f'labelled %: \n {l_total_percent[j]}')
            print(f'geo-rec %: \n {g_total_percent[j]}')
            print(f'items: \n {items_in_bed[j]}'
                  f'\n')
            return

        l_total_percent[j] = int(l_total_percent[j] / items_in_bed[j] * 100)

        g_total_percent[j] = int(g_total_percent[j] / items_in_bed[j] * 100)

        # -------------------------------------------------------
        # get species and alltab_genus count from species list
        bed_group = species_in_bed[j]

        # count species incl. subspecies
        species_cnt = len(bed_group)
        species_cnts.append(species_cnt)

    # -------------------------------------------------------

    # specify dtype to save memory
    df = pd.DataFrame({'Bed': pd.Series(beds),  # each string occurs only once
                       'Species Count': pd.Series(species_cnts, dtype='int16'),
                       'Item Count': pd.Series(items_in_bed, dtype='int16'),
                       'Label Stats': pd.Series(l_total_percent, dtype='int8'),
                       'Geo-record Stats': pd.Series(g_total_percent, dtype='int8'),
                       L_ONLY: pd.Series(l, dtype='int16'),
                       G_ONLY: pd.Series(g, dtype='int16'),
                       L_AND_G: pd.Series(lg, dtype='int16'),
                       NOT_L_NOR_G: pd.Series(not_lg, dtype='int16'),
                       LGPF: pd.Series(lgr, dtype='int16')
                       })
    df.set_index('Bed')

    '''
    # clock
    parse_data_end = tim.time()
    # check memory
    memory = df.memory_usage(deep=True)

    print(f'Time taken to parse csv df into plottable df: {(parse_data_end - start):f}.\n'
          f'Memory used: \n{memory}.')'''

    return df


# -------------------------------------------------------
# helper to reduce code duplication
def process_item(yes_action, no_action, labelled, georecorded, age, l_total, g_total, lg, lgr, not_lg, l, g):
    if labelled:  # total labelled
        yes_action(l_total)
        # we have not converted the counts to a percentage yet! will do after knowing item count per bed
    else:
        no_action(l_total)

    if georecorded:  # total georecorded
        yes_action(g_total)
    else:
        no_action(g_total)

    if labelled and georecorded:
        yes_action(lg)
    else:
        no_action(lg)

    if labelled and georecorded and age < FUZZY_AGE:
        yes_action(lgr)
    else:
        no_action(lgr)

    if not (labelled or georecorded):
        yes_action(not_lg)
    else:
        no_action(not_lg)

    if labelled and not georecorded:
        yes_action(l)
    else:
        no_action(l)

    if georecorded and not labelled:
        yes_action(g)
    else:
        no_action(g)


# -------------------------------------------------------
# make sure make_df loop is run only once. same with mock
# I see that it gets run twice anyways: before building flask app and after

if len(CACHE) == 0:
    for genus in GENUS:
        CACHE.append(make_df(genus))

# df = CACHE[0]
# sunburst = df[[L_ONLY,G_ONLY,L_AND_G,LGPF,NOT_L_NOR_G]]

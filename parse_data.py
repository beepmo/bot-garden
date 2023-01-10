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
# store for today, before new csv drops tomorrow
CACHE = []


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

# -------------------------------------------------------
# create one row of attributes for each bed


def make_df(genus):  # genus is string
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

        try:
            # bed is in beds
            bed_location = beds.index(bed)

            # update tags
            if labelled:  # total labelled
                l_total_percent[bed_location] += 1
                # we have not converted the counts to a percentage yet! will do after knowing item count per bed

                if georecorded:  # labelled & geo-recorded
                    lg[bed_location] += 1

                    if age < FUZZY_AGE:  # labelled & geo-recorded & reported post-fuzzy
                        lgr[bed_location] = lgr[bed_location] + 1

                else:  # not labelled; geo-recorded only
                    l[bed_location] += 1

            if georecorded:  # total geo-recorded
                g_total_percent[bed_location] += 1

            # update item count
            items_in_bed[bed_location] += 1

            # update species
            in_this_bed = species_in_bed[bed_location]
            if not species in in_this_bed:
                in_this_bed.append(species)

        except ValueError:
            # bed is not in beds

            # add bed to beds
            beds.append(bed)

            # add species as list
            species_in_bed.append([species])

            # count item as list
            items_in_bed.append(1)

            # add tag baskets
            if labelled:  # total labelled
                l_total_percent.append(1)
                # we have not converted the counts to a percentage yet! will do after knowing item count per bed

                if georecorded:  # labelled & geo-recorded
                    lg.append(1)

                    if age < FUZZY_AGE:  # labelled & geo-recorded & reported post-fuzzy
                        lgr.append(1)
                    else:
                        lgr.append(0)

                else:
                    lg.append(0)

            else:
                l_total_percent.append(0)

            if georecorded:
                g_total_percent.append(1)
            else:
                g_total_percent.append(0)

    assert 'HUBC' not in beds

    # -------------------------------------------------------
    # turn counts into plottable

    # species count by bed, in same order as beds
    species_cnts = []

    for j in range(len(beds)):
        # -------------------------------------------------------
        # get tag as int percentage
        l_total_percent[j] = int(l_total_percent[j] / items_in_bed[j] * 100)
        g_total_percent[j] = int(g_total_percent[j] / items_in_bed[j] * 100)

        # -------------------------------------------------------
        # get species and genus count from species list
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
                       })
    df.set_index('Bed')

    # clock
    parse_data_end = tim.time()
    # check memory
    memory = df.memory_usage(deep=True)

    print(f'Time taken to parse csv df into plottable df: {(parse_data_end - start):f}.\n'
          f'Memory used: \n{memory}.')

    return df


# ______________________________________________________
# helpers

# affirmative action for item in known bed
def increment_here(list, index):
    list[index] += 1


# negative action for item in new (insofar unknown) bed
def do_nothing():
    pass


# affirmative action for item in new (insofar unknown) bed
def append_1(list):
    list.append(1)


# negative action for item in new (insofar unknown) bed
def append_0(list):
    list.append(0)


def process_item(yes_action, no_action, labelled, georecorded, age):
    if labelled:  # total labelled
        yes_action(l_total_percent)
        # we have not converted the counts to a percentage yet! will do after knowing item count per bed

    if georecorded:  # total georecorded
        yes_action(g_total_percent)


# -------------------------------------------------------
# make sure make_df loop is run only once. same with mock
# I see that it gets run twice anyways: before building flask app and after

if len(CACHE) == 0:
    for g in GENUS:
        CACHE.append(make_df(g))

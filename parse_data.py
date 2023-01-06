import time as tim
import pandas as pd

from request_csv import csv_pddf
from datetime import datetime

# -------------------------------------------------------
# Parse constants that control what data we display

# client-specified time before which data is less reliable
FUZZY = datetime.strptime('2016', '%Y')
delta_fuzzy = datetime.today() - FUZZY
FUZZY_AGE = delta_fuzzy.days

# number of days considered recent
RECENT = 365

GENUS = ('',
         'Acer',
         'Magnolia',
         'Rhododendron',
         'Cornus',
         'Sorbus',
         'Clematis',
         )

ATTRIBUTES = ('Species Count', 'Item Count', 'Label Stats', 'Geo-record Stats')

# -------------------------------------------------------
# store for today, before new csv drops tomorrow
CACHE = []

# -------------------------------------------------------


# create one row of attributes for each bed
def make_df(genus, fuzzy_age, recent):  # genus is string
    start = tim.time()

    # list of beds
    beds = []
    # lists in which the ith entry corresponds to the ith bed in beds:
    # list of species lists
    species_per_bed = []
    # list of numbers
    items_per_bed = []
    label_pc_per_bed = []  # int percentage of items labelled
    geo_pc_per_bed = []  # int percentage of items geo-recorded
    post_fuzzy_per_bed = []  # number of items reported after fuzzy date
    recent_per_bed = []  # number of items reported recently

    # populate the lists bed and species_per_bed
    for index, row in csv_pddf.iterrows():  # iterate over all rows of data
        species = row['Taxon']

        if genus and (species.partition(' ')[0] != genus):
            continue

        bed = row['Bed']
        # just for this data source
        if bed == 'HUBC':
            continue

        labelled = row['Label']
        georecorded = row['Geo?']
        age = row['Days Since Sighted']

        try:
            # bed is in beds
            bed_location = beds.index(bed)

            # update tags
            if labelled:
                label_pc_per_bed[bed_location] = label_pc_per_bed[bed_location] + 1
            if georecorded:
                geo_pc_per_bed[bed_location] = geo_pc_per_bed[bed_location] + 1

            # update item count
            items_per_bed[bed_location] = items_per_bed[bed_location] + 1

            # update datetime things


            # update species
            in_this_bed = species_per_bed[bed_location]
            if not species in in_this_bed:
                in_this_bed.append(species)

        except ValueError:
            # bed is not in beds

            # add bed to beds
            beds.append(bed)

            # add species as list
            species_per_bed.append([species])

            # count item as list
            items_per_bed.append(1)

            # add tag baskets
            if labelled:
                label_pc_per_bed.append(1)
            else:
                label_pc_per_bed.append(0)

            if georecorded:
                geo_pc_per_bed.append(1)
            else:
                geo_pc_per_bed.append(0)

    assert 'HUBC' not in beds

    # -------------------------------------------------------
    # turn counts into plottable

    # species count by bed, in same order as beds
    species_cnts = []

    for j in range(len(beds)):
        # -------------------------------------------------------
        # get tag as int percentage
        label_pc_per_bed[j] = int(label_pc_per_bed[j] / items_per_bed[j] * 100)
        geo_pc_per_bed[j] = int(geo_pc_per_bed[j] / items_per_bed[j] * 100)

        # -------------------------------------------------------
        # get species and genus count from species list
        bed_group = species_per_bed[j]

        # count species incl. subspecies
        species_cnt = len(bed_group)
        species_cnts.append(species_cnt)

    # -------------------------------------------------------

    # specify dtype to save memory
    df = pd.DataFrame({'Bed': pd.Series(beds),  # each string occurs only once
                       'Species Count': pd.Series(species_cnts, dtype='int16'),
                       'Item Count': pd.Series(items_per_bed, dtype='int16'),
                       'Label Stats': pd.Series(label_pc_per_bed, dtype='int8'),
                       'Geo-record Stats': pd.Series(geo_pc_per_bed, dtype='int8'),
                       })

    # clock
    parse_data_end = tim.time()
    # check memory
    memory = df.memory_usage(deep=True)

    print(f'Time taken to parse csv df into plottable df: {(parse_data_end - start):f}.\n'
          f'Memory used: \n {memory}.')

    return df


# make sure make_df loop is run only once. same with mock
# I see that it gets run twice anyways: before building flask app and after

if len(CACHE) == 0:
    for g in GENUS:
        CACHE.append(make_df(g, FUZZY_AGE, RECENT))

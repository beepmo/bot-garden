import time as tim
import pandas as pd

from request_csv import csv_pddf


def make_df(genus):  # genus is string
    start = tim.time()

    # list of beds
    beds = []
    # lists in which the ith entry corresponds to the ith bed in beds:
    # list of species lists
    species_in_bed = []
    # list of numbers
    items_in_bed = []
    labelled_in_bed = []
    georecorded_in_bed = []
    # list of strin lists
    ages_in_bed = []

    # populate the lists bed and species_in_bed
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
                labelled_in_bed[bed_location] = labelled_in_bed[bed_location] + 1
            if georecorded:
                georecorded_in_bed[bed_location] = georecorded_in_bed[bed_location] + 1

            # update days since sighting
            ages_in_bed[bed_location].append(age)

            # update item count
            items_in_bed[bed_location] = items_in_bed[bed_location] + 1

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

            # add age as list
            ages_in_bed.append([age])

            # count item as list
            items_in_bed.append(1)

            # add tag baskets
            if labelled:
                labelled_in_bed.append(1)
            else:
                labelled_in_bed.append(0)

            if georecorded:
                georecorded_in_bed.append(1)
            else:
                georecorded_in_bed.append(0)

    assert 'HUBC' not in beds

    # -------------------------------------------------------
    # turn counts into plottable

    # species count by bed, in same order as beds
    species_cnts = []

    for j in range(len(beds)):
        # -------------------------------------------------------
        # get tag as int percentage
        labelled_in_bed[j] = int(labelled_in_bed[j]/items_in_bed[j] * 100)
        georecorded_in_bed[j] = int(georecorded_in_bed[j]/items_in_bed[j] * 100)

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
                       'Label Stats': pd.Series(labelled_in_bed, dtype='int8'),
                       'Geo-record Stats': pd.Series(georecorded_in_bed, dtype='int8'),
                       'Days since sightings': pd.Series(ages_in_bed)
                       })
    # put attributes list here to manually update
    attributes = ['Species Count', 'Item Count', 'Label Stats', 'Geo-record Stats']
    # clock
    parse_data_end = tim.time()
    # check memory
    memory = df.memory_usage(deep=True)

    print(f'Time taken to parse csv df into plottable df: {(parse_data_end - start):f}.\n'
          f'Memory used: \n {memory}.')

    return df, attributes


# make sure make_df is run only once. same with mock
# I see that it gets run twice anyways: before building flask app and after
df_shelf = ()

if len(df_shelf) == 0:
    df_shelf = make_df('')
    all_genus_df = df_shelf[0]
    attributes = df_shelf[1]
else:
    assert len(df_shelf) == 2
    all_genus_df = df_shelf[0]
    attributes = df_shelf[1]

import time as tim
import pandas as pd

from request_csv import csv_pddf


def make_df():
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
        bed = row['Bed']
        species = row['Taxon']
        labelled = row['Label']
        georecorded = row['Geo?']
        age = row['Days Since Sighted']

        if bed == 'HUBC':
            continue

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

    # species count by bed, in same order as beds
    species_cnts = []
    # genus count by bed, in same order as beds
    genus_cnts = []

    # get species and genus count from species list
    for bed_group in species_in_bed:
        # count species incl. subspecies
        species_cnt = len(bed_group)
        species_cnts.append(species_cnt)

        # count genus (first word before space)
        unique = set()
        for i in range(len(bed_group)):
            genus = bed_group[i].partition(' ')[0]
            unique.add(genus)

        genus_cnt = len(unique)
        genus_cnts.append(genus_cnt)

    # specify dtype to save memory
    df = pd.DataFrame({'Bed': pd.Series(beds),  # each string occurs only once
                       'Species Count': pd.Series(species_cnts, dtype='int16'),
                       'Genus Count': pd.Series(genus_cnts, dtype='int16'),
                       'Item Count': pd.Series(items_in_bed, dtype='int16'),
                       'Label Count': pd.Series(labelled_in_bed, dtype='int16'),
                       'Geo-record Count': pd.Series(georecorded_in_bed, dtype='int16'),
                       'Days since sightings': pd.Series(ages_in_bed)
                       })
    # put attributes list here to manually update
    # TODO update
    attributes = ['Bed', 'Species Count', 'Genus Count']
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
    df_shelf = make_df()
    df = df_shelf[0]
    attributes = df_shelf[1]
else:
    assert len(df_shelf) == 2
    df = df_shelf[0]
    attributes = df_shelf[1]

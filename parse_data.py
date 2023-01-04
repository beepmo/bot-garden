import time

import pandas as pd
from unittest.mock import Mock

from request_csv import csv_pddf


def make_df():
    parse_data_start = time.time()

    # list of bed
    beds = []
    # list of species list, same order as list of bed
    species_in_bed = []

    # populate the lists bed and species_in_bed
    for index, row in csv_pddf.iterrows():  # iterate over all rows of data
        bed = row['Bed']
        species = row['Taxon']
        label = row['Label']

        if bed == 'HUBC':
            continue

        try:
            # bed is in beds
            bed_location = beds.index(bed)

            in_this_bed = species_in_bed[bed_location]
            if not species in in_this_bed:
                in_this_bed.append(species)
        except ValueError:
            # bed is not in beds
            # add bed to beds
            beds.append(bed)
            # add species as list
            species_in_bed.append([species])

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

    # convert to pandas dataframe
    # dict_of_lists = {'Bed': beds,
    #                  'Species Count': species_cnts,
    #                  'Genus Count': genus_cnts
    #                  }

    df = pd.DataFrame({'Bed': pd.Series(beds),
                       'Species Count': pd.Series(species_cnts, dtype='int16'),
                       'Genus Count': pd.Series(species_cnts, dtype='int16')
                       })
    memory = df.memory_usage()

    attributes = ['Bed', 'Species Count', 'Genus Count']

    # memoize the columns in the parsed data
    # attributes = set(dict_of_lists.keys())
    # attributes.remove('Bed')

    # do not replace raw data csv_pddf
    # noinspection PyTypeChecker
    # df = pd.DataFrame.from_dict(dict_of_lists,
    #                             dtype='int16')

    parse_data_end = time.time()

    time = parse_data_end - parse_data_start
    print(time,type(time))
    print(f'Time taken to parse csv df into plottable df: {(parse_data_end - parse_data_start)}.'
          f'Memory used: {(memory):f}.')
    print(df.head())

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
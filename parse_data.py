import time as tim
import pandas as pd

from request_csv import csv_pddf


def make_df():
    start = tim.time()

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

    # memoize the columns in the parsed data
    # attributes = set(dict_of_lists.keys())
    # attributes.remove('Bed')

    # df = pd.DataFrame.from_dict(dict_of_lists)

    # specify dtype to save memory
    df = pd.DataFrame({'Bed': pd.Series(beds),  # each string occurs only once
                       'Species Count': pd.Series(species_cnts, dtype='int64'),
                       'Genus Count': pd.Series(species_cnts, dtype='int64')
                       })
    # put attributes list here to manually update
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

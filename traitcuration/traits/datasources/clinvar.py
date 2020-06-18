"""
This module contains utility functions for downloading, parsing and storing trait data fron ClinVar
"""

import urllib.request
import csv
import gzip
import itertools
import os

from ..models import Trait

URL = 'https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz'


def download_clinvar_data():
    """
    This function downloads the latest ClinVar TSV release data and extracts it into a 'variant_summary.txt' file
    """
    print("Downloading ClinVar data...")
    urllib.request.urlretrieve(URL, './variant_summary.txt.gz')


def parse_trait_names_and_source_records():
    """
    This function parses a downloaded 'variant_summary.txt' file, and returns a unique set of traint names
    along with their calculated source record number, in a form of a dictionary where the key is the trait name
    and the value is the source record number.
    """
    print("Parsing ClinVar data...")
    with gzip.open('variant_summary.txt.gz', 'rt') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        # A dictionary with trait names as keys and sets of source records as values
        traits_dict = dict()
        # The int value here defines how many records should be parsed
        for row in itertools.islice(reader, 10):
            # For every row, get its allele_id and all its rcv_accessions and phenotypes
            row_alleleid = (row['#AlleleID'])
            row_rcv_list = row['RCVaccession'].split(';')
            row_phenotype_list = row['PhenotypeList'].split(';')
            # Get every possible pair tuple of allele_id rcv_accessions and phenotypes for the current row
            tuple_set = set()
            for index in range(len(row_rcv_list)):
                tuple_set.add(
                    (row_alleleid, row_rcv_list[index], row_phenotype_list[index]))
            # Insert the tuple in the dictionary
            for tuple in tuple_set:
                trait_name = tuple[2]
                if trait_name in traits_dict:
                    traits_dict[trait_name].update([tuple])
                else:
                    traits_dict[trait_name] = {tuple}
        # Count the number of source records for each trait name
        for key in traits_dict.keys():
            traits_dict[key] = len(traits_dict[key])
        os.remove("variant_summary.txt.gz")
        return traits_dict


def store_data(traits_dict):
    """
    This function accepts a dictionary in the form of keys=trait names and values=source record numbers
    and stores them in the database using the Django ORM.
    """
    print("Storing ClinVar data...")
    for trait_name in traits_dict.keys():
        if Trait.objects.filter(name=trait_name).exists():
            trait = Trait.objects.filter(name=trait_name).first()
            trait.number_of_source_records = traits_dict[trait_name]
            trait.save()
        else:
            trait = Trait(name=trait_name, status="unmapped",
                          number_of_source_records=traits_dict[trait_name])
            trait.save()

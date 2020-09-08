"""
This module contains utility functions for downloading, parsing and storing trait data fron ClinVar
"""
import traceback
import csv
import gzip
import itertools
import os
import logging
import requests

from django.db import transaction

from ..models import Trait, Status

# Constants to use. URL defines the clinvar data location and NUMBER_OF_RECORDS defines how many traits to parse
# during development.
URL = 'https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz'
NUMBER_OF_RECORDS = 1000

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run_clinvar():
    """
    This function initiates the process of downloading, parsing and storing ClinVar data
    """
    try:
        download_clinvar_data()
        traits_dict = parse_trait_names_and_source_records()
        store_data(traits_dict)
    except Exception:
        track = traceback.format_exc()
        logger.error(track)
        return


def download_clinvar_data():
    """
    This function downloads the latest ClinVar TSV release data and extracts it into a 'variant_summary.txt' file
    """
    logger.info("Downloading ClinVar data...")
    r = requests.get(URL, allow_redirects=True)
    open('variant_summary.txt.gz', 'wb').write(r.content)


def parse_trait_names_and_source_records():
    """
    This function parses a downloaded 'variant_summary.txt' file, and returns a unique set of trait names
    along with their calculated source record number, in a form of a dictionary where the key is the trait name
    and the value is the source record number.
    """
    logger.info("Parsing ClinVar data...")
    with gzip.open('variant_summary.txt.gz', 'rt') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        # A dictionary with trait names as keys and sets of source records as values
        traits_dict = dict()
        # The int value here defines how many records should be parsed
        for row in itertools.islice(reader, NUMBER_OF_RECORDS):
            # For every row, get its allele_id and all its rcv_accessions and phenotypes
            row_alleleid = (row['#AlleleID'])
            row_rcv_list = row['RCVaccession'].split('|')
            row_phenotype_list = row['PhenotypeList'].split('|')
            if '-' in row_phenotype_list:
                row_phenotype_list.remove('-')
            if len(row_phenotype_list) > 5:
                continue
            # Get every possible pair tuple of allele_id rcv_accessions and phenotypes for the current row
            tuple_set = {(row_alleleid, rcv, phenotype) for rcv, phenotype in zip(row_rcv_list, row_phenotype_list)}
            # Insert the tuple in the dictionary
            for tuple in tuple_set:
                trait_name = tuple[2]
                traits_dict.setdefault(trait_name, set())
                traits_dict[trait_name].update([tuple])
        # Count the number of source records for each trait name
        for key in traits_dict.keys():
            traits_dict[key] = len(traits_dict[key])
        os.remove("variant_summary.txt.gz")
        return traits_dict


@transaction.atomic
def store_data(traits_dict):
    """
    This function accepts a dictionary in the form of keys=trait names and values=source record numbers
    and stores them in the database using the Django ORM.
    """
    logger.info("Storing ClinVar data...")
    for trait_name in traits_dict.keys():
        if Trait.objects.filter(name=trait_name).exists():
            trait = Trait.objects.filter(name=trait_name).first()
            trait.number_of_source_records = traits_dict[trait_name]
        else:
            trait = Trait(name=trait_name, status=Status.UNMAPPED,
                          number_of_source_records=traits_dict[trait_name])
        trait.save()

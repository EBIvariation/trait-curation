import urllib.request
import csv
import gzip
import shutil
import itertools
import os
from ..models import Trait


def extract_clinvar_data():
    """
    This function downloads the latest ClinVar TSV release data and extracts it into a 
    'variant_summary.txt' file
    """
    print("Downloading ClinVar data...")
    url = 'https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz'
    urllib.request.urlretrieve(url, './variant_summary.txt.gz')
    print("Extracting ClinVar data...")
    with gzip.open('variant_summary.txt.gz', 'rb') as f_in:
        with open('variant_summary.txt', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def parse_trait_names_and_source_records():
    """
    This function parses a downloaded 'variant_summary.txt' file, and returns a unique set of traint names
    along with their calculated source record number, in a form of a dictionary where the key is the trait name
    and the value is the source record number
    """
    print("Parsing ClinVar data...")
    with open('variant_summary.txt') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        # A dictionary with trait names as keys and sets of source records as values
        traits_dict = dict()
        # The int value here defines how many records should be parsed
        for row in itertools.islice(reader, 10):
            # For every row, get its allele_id and all its rcv_accessions and phenotypes
            row_alleleid = [(row['#AlleleID'])]
            row_rcv_list = set(row['RCVaccession'].split(';'))
            row_phenotype_list = set(row['PhenotypeList'].split(';'))
            # Get every possible combination tuple of allele_id rcv_accessions and phenotypes for the current row
            tuple_list = list(itertools.product(
                row_alleleid, row_rcv_list, row_phenotype_list))
            # Insert the tuple in the dictionary
            for tuple in tuple_list:
                trait_name = tuple[2]
                if trait_name in traits_dict:
                    traits_dict[trait_name].update([tuple])
                else:
                    traits_dict[trait_name] = {tuple}
        # Count the number of source records for each trait name
        for key in traits_dict.keys():
            traits_dict[key] = len(traits_dict[key])
        os.remove("variant_summary.txt")
        os.remove("variant_summary.txt.gz")
        return traits_dict


def store_data(traits_dict):
    """
    This function accepts a dictionary in the form of keys=trait names and values=source record numbers
    and stores them in the database using the Django ORM
    """
    print("Storing ClinVar data...")
    try:
        for trait_name in traits_dict.keys():
            print(trait_name)
            if Trait.objects.filter(name=trait_name).exists():
                trait = Trait.objects.filter(name=trait_name).first()
                trait.number_of_source_records = traits_dict[trait_name]
                trait.save()
            else:
                trait = Trait(name=trait_name, status="unmapped",
                              number_of_source_records=traits_dict[trait_name])
                trait.save()
    except Exception as e:
        print(f"Error: {e}")

import requests
import traceback
import logging

from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .datasources import zooma, clinvar, ols
from .models import Trait
from .utils import create_spreadsheet_and_issue


logging.basicConfig()
logger = logging.getLogger('clinvar')
logger.setLevel(logging.INFO)


@shared_task(bind=True)
def import_zooma(self):
    try:
        progress_recorder = ProgressRecorder(self)
        traits = Trait.objects.all()
        for index, trait in enumerate(traits):
            zooma.run_zooma_for_single_trait(trait)
            progress_recorder.set_progress(index, len(traits))
        return 'Successful Import'
    except Exception as e:
        track = traceback.format_exc()
        logger.error(track)
        progress_recorder.stop_task(100, 100, e)
        return


@shared_task(bind=True)
def import_clinvar(self):
    progress_recorder = ProgressRecorder(self)
    try:
        with open('variant_summary.txt.gz', "wb") as f:
            logger.info("Downloading ClinVar data...")
            response = requests.get(clinvar.URL, allow_redirects=True, stream=True)
            total_length = response.headers.get('content-length')
            total_length_mb = int(total_length) / 1000000
            downloaded_mb = 0
            for data in response.iter_content(chunk_size=4096):
                downloaded_mb += len(data) / 1000000
                f.write(data)
                progress_recorder.set_progress(round(downloaded_mb, 2), round(total_length_mb, 2))
            traits_dict = clinvar.parse_trait_names_and_source_records()
            clinvar.store_data(traits_dict)
            return 'Successful Import'
    except Exception as e:
        track = traceback.format_exc()
        logger.error(track)
        progress_recorder.stop_task(100, 100, e)
        return


@shared_task
def get_clinvar_data_and_suggestions():
    clinvar.run_clinvar()
    zooma.run_zooma_for_all_traits()
    return 'Successful Import'


@shared_task
def import_ols():
    ols.ols_update()
    return 'Successful status update'


@shared_task
def create_github_issue(github_access_token, issue_info):
    issue_url = create_spreadsheet_and_issue(github_access_token, issue_info)
    return issue_url

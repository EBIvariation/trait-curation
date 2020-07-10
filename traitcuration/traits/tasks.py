from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .datasources import zooma, clinvar
from .models import Trait


@shared_task(bind=True)
def get_zooma_suggestions(self):
    progress_recorder = ProgressRecorder(self)
    traits = Trait.objects.all()
    for index, trait in enumerate(traits):
        zooma.run_zooma_for_single_trait(trait)
        progress_recorder.set_progress(index, len(traits))
    return 'Successful Import'


@shared_task
def get_clinvar_data():
    clinvar.run_clinvar()
    return 'Successful Import'


@shared_task
def get_clinvar_data_and_suggestions():
    clinvar.run_clinvar()
    zooma.run_zooma_for_all_traits()
    return 'Successful Import'

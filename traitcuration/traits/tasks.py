from __future__ import absolute_import

from celery import shared_task
from .datasources import zooma, clinvar


@shared_task
def get_zooma_suggestions():
    zooma.get_zooma_suggestions()


@shared_task
def get_clinvar_data():
    clinvar.run_clinvar()


@shared_task
def get_clinvar_data_and_suggestions():
    clinvar.run_clinvar()
    zooma.get_zooma_suggestions()

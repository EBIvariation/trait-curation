from django_admin_conf_vars.global_vars import config

config.set("CLINVAR_BASE_URL", default='https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz')
config.set("CLINVAR_RECORDS_TO_PARSE", default=1000)

config.set("ZOOMA_BASE_URL", default="http://www.ebi.ac.uk/spot/zooma/v2/api")

config.set("OXO_BASE_URL", default="https://www.ebi.ac.uk/spot/oxo/api/search?size=5000")
config.set("OXO_MAPPING_DISTANCE", default=2)

config.set("REVIEW_MIN_NUMBER", default=2)

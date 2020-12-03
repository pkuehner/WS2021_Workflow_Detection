import pandas as pd

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import sorting
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter


# import xes and sort the event log by timestamps
def import_xes(path):
    log = xes_importer.apply(path)
    log = sorting.sort_timestamp(log)
    return log

# import csv and sort the event log by timestamps
def import_csv(path):
    log_csv = pd.read_csv(path, sep=',')
    log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
    #parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'Case ID'}
    log_csv = log_csv.sort_values('time:timestamp')
    event_log = log_converter.apply(log_csv)#, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)
    return event_log


import create_wf_model as pt_converter
import pandas as pd
from bpmn_visualizer import graphviz_visualization as bpmn_visualizer
from pattern_util import pattern_finder
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.conversion.process_tree import converter as bpmn_converter
from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.objects.log.util import dataframe_utils
from pm4py.visualization.common import save as gsave
from pm4py.visualization.petrinet import visualizer as pn_visualizer
from wf_pattern_visualizer import graphviz_visualization as wf_visualizer


def import_csv(file_path):
    """
    Import an event log in csv format
    Parameters
    --------------
    file_path
        path to the event log
    Returns
    --------------
    log
        log object
    """
    log_csv = pd.read_csv(file_path, sep=',')
    log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
    log = log_converter.apply(log_csv)
    return log


def discover_wf_model(log_path, model_name):
    """
    Discover the workflow pattern inside an event log
    Parameters
    --------------
    log_path
        path to the event log
    model_name
        name of the wf models
    Returns
    --------------
    model_path
        path to the discovered wf pattern models
    """
    log = xes_import.apply(log_path)
    ptree = inductive_miner.apply_tree(log)
    wf_model = pt_converter.apply(ptree)
    gviz = wf_visualizer(wf_model)
    model_path = 'model/' + model_name + '.png'
    gsave.save(gviz, model_path)
    return model_path


def discover_pn_model(log_path, model_name):
    """
    Discover the petrinet models for an event log
    Parameters
    --------------
    log_path
        path to the event log
    model_name
        name of the pn models
    Returns
    --------------
    model_path
        path to the discovered pn models
    """
    log = xes_import.apply(log_path)
    net, initial_marking, final_marking = inductive_miner.apply(log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking, variant=pn_visualizer.Variants.FREQUENCY, log=log)
    model_path = 'model/' + model_name + '.png'
    pn_visualizer.save(gviz, model_path)
    return model_path


def discover_bpmn_model(log_path, model_name):
    """
    Discover the BPMN for an event log
    Parameters
    --------------
    log_path
        path to the event log
    model_name
        name of the BPMN
    Returns
    --------------
    model_path
        path to the discovered BPMN
    """
    log = xes_import.apply(log_path)
    ptree = inductive_miner.apply_tree(log)
    bpmn = bpmn_converter.apply(ptree, variant=bpmn_converter.Variants.TO_BPMN)
    gviz = bpmn_visualizer(bpmn)
    model_path = 'model/' + model_name + '.png'
    gsave.save(gviz, model_path)
    return model_path


def discover_patterns(log_path, model_name):
    """
    Discover the petrinet models for an event log
    Parameters
    --------------
    log_path
        path to the event log
    model_name
        name of the pn models
    Returns
    --------------
    patterns_as_json
    """
    log = xes_import.apply(log_path)
    ptree = inductive_miner.apply_tree(log)
    wf_model = pt_converter.apply(ptree)
    p_finder = pattern_finder(wf_model)
    return p_finder.patterns_to_json()

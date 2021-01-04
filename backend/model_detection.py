import create_wf_model  as pt_converter
from pattern_util import pattern_finder
from importer import import_file
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.process_tree import converter as bpmn_converter
from pm4py.visualization.common import save as gsave
from pm4py.visualization.petrinet import visualizer as pn_vis
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from wf_pattern_visualizer import graphviz_visualization as wf_visualizer
import json


def discover_wf_model(log_path, model_name, patterns_to_merge = None, pattern_to_color={}):
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
    log = import_file(log_path, False)
    ptree = inductive_miner.apply_tree(log)
    wf_model = pt_converter.apply(ptree)
    p_finder = pattern_finder(wf_model)
    if patterns_to_merge:
        print(patterns_to_merge)
        patterns_to_merge = json.loads(patterns_to_merge)
        for pattern in patterns_to_merge:
            print(pattern)
            p_finder.merge_join(pattern)
    gviz = wf_visualizer(p_finder.wf_model, loop_nodes=p_finder.get_loops(), pattern_to_color=pattern_to_color)
    model_path = 'models/' + model_name + '.png'
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
    log = import_file(log_path, False)
    net, initial_marking, final_marking = inductive_miner.apply(log, variant=inductive_miner.Variants.IM)
    gviz = pn_vis.apply(net, initial_marking, final_marking)
    model_path = 'models/' + model_name + '.png'
    pn_vis.save(gviz, model_path)
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
    log = import_file(log_path, False)
    ptree = inductive_miner.apply_tree(log)
    bpmn = bpmn_converter.apply(ptree, variant=bpmn_converter.Variants.TO_BPMN)
    gviz = bpmn_visualizer.apply(bpmn)
    model_path = 'models/' + model_name + '.png'
    gsave.save(gviz, model_path)
    return model_path


def discover_patterns(log_path, pattern_id = None):
    """
    Discover the patterns for an event log
    Parameters
    --------------
    log_path
        path to the event log
    pattern_id
        ids of the pattern that should be merged
    Returns
    --------------
    patterns_as_json
    """
    log = import_file(log_path, False)
    ptree = inductive_miner.apply_tree(log)
    wf_model = pt_converter.apply(ptree)
    p_finder = pattern_finder(wf_model)
    if pattern_id:
        p_finder.merge_join(pattern_id)
    return p_finder.patterns_to_json()

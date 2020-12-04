import create_wf_model as pt_converter
from wf_pattern_visualizer import graphviz_visualization
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.visualization.common import gview

def import_log(filename):
    log = xes_import.apply(filename)
    return log

def discover_wf_model():
    log = xes_import.apply("test-data/running-example.xes")
    ptree = inductive_miner.apply_tree(log)
    wf_model = pt_converter.apply(ptree)
    gviz = graphviz_visualization(wf_model)
    gview.view(gviz)

discover_wf_model()

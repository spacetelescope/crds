"""This module is used to generate the SYSTEM CRDSCFG reference file.  The code
is directly edited and the module itself is run to emit a new reference as in:

$ python -m crds.jwst.gen_system_crdscfg  updated_inputs.yaml  >new_reference.yaml

Suggested approach for obtaining updated inputs is downloading the most current
SYSTEM CRDSCFG reference file and updating MANUAL sections.

Current calibration code must be available in order to automatically
regenerates since CRDS will inspect the installed .cfg files to determine Step
configurations and required reference types.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import re
import fnmatch

# ----------------------------------------------------------------------------------------------

import yaml

# ----------------------------------------------------------------------------------------------

from jwst import version
from jwst.stpipe import cmdline as jwst_cmdline

# ----------------------------------------------------------------------------------------------

from crds.core import log, exceptions, utils, timestamp
from crds.core.log import srepr

# ----------------------------------------------------------------------------------------------
VERSION_RE_STR = r"(\d+\.\d+.\d+).*"

CAL_VER = re.match(r"^" + VERSION_RE_STR, version.__version__).group(1)

GENERATION_DATE = timestamp.now("T").split(".")[0]

REFERENCE_DIVIDER = "# vvvvvvvv GENERATED vvvvvvvv"

# --------------------------------------------------------------------------------------

class CrdsCfgGenerator(object):
    """Used to re-generate SYSTEM CRDSCFG reference files based on modified
    versions of previous reference files.
    """
    def __init__(self, input_yaml):
        self.input_yaml = input_yaml
        self.loaded_cfg = self.get_body()
        self.levels = self.loaded_cfg.levels
        self.exp_types = self.loaded_cfg.exp_types
        self.pipeline_cfgs_to_steps = {}
        self.steps_to_reftypes = {}
        self.generate_pipeline_info()
        self.exptypes_to_cfgs = { exp_type : self.exptype_to_pipelines(exp_type) 
                                  for exp_type in self.exp_types }
        self.exptypes_to_reftypes = { exp_type : self.exptype_to_reftypes(exp_type) 
                                      for exp_type in self.exp_types }

    def get_body(self):
        """Load the input_yaml as a CRDS Struct and return it."""
        return utils.Struct(yaml.load(self.input_yaml))
    
    def get_updated_yaml(self):
        """Modify the input_yaml to replace the cal code version and generation date,
        useful for updating an existing reference and running it through this generator.
        """
        input_body = []
        for line in self.input_yaml.splitlines():
            if line.strip().startswith("calibration_software_version:"):
                input_body += ["    calibration_software_version: " + CAL_VER]
            elif line.strip().startswith("generation_date:"):
                input_body += ["    generation_date: " + GENERATION_DATE]
            else:
                input_body += [line]
        return "\n".join(input_body).split(REFERENCE_DIVIDER)[0] + "\n" + REFERENCE_DIVIDER + "\n"
    
    def generate_pipeline_info(self):
        """Based on the input YAML and JWST cal code,  generate the mappings:
        pipeline_cfgs_to_steps
        steps_to_reftypes
        """
        self.pipeline_cfgs_to_steps["skip_2b.cfg"] = []
        for pipeline_cfg in self.loaded_cfg.pipeline_cfgs:
            steps_to_reftypes = jwst_cmdline.steps_to_reftypes_from_config(pipeline_cfg)
            self.pipeline_cfgs_to_steps[pipeline_cfg] = sorted(list(steps_to_reftypes.keys()))
            self.steps_to_reftypes.update(steps_to_reftypes)
        
    def generate_output_yaml(self):
        """Generate the SYSTEM CRDSCFG reference YAML."""
        output_yaml = self.get_updated_yaml()
        output_yaml += yaml.dump({"pipeline_cfgs_to_steps" : self.pipeline_cfgs_to_steps}) + "\n"
        output_yaml += yaml.dump({"steps_to_reftypes" : self.steps_to_reftypes}) + "\n"
        output_yaml += yaml.dump({"exptypes_to_pipelines" : self.exptypes_to_cfgs}) + "\n"
        output_yaml += yaml.dump({"exptypes_to_reftypes" : self.exptypes_to_reftypes}) + "\n"
        return output_yaml
    
    def __str__(self):
        return self.generate_output_yaml()
    
    def exptype_to_pipelines(self, exp_type):
        """For a given EXP_TYPE string, return a list of reftypes needed to process that
        EXP_TYPE through the data levels appropriate for that EXP_TYPE.
    
        Return [reftypes... ]
        """
        pipelines = []
        for level in self.levels:
            pipelines.extend(self.get_level_pipeline(level, exp_type))
        return pipelines

    def exptype_to_reftypes(self, exp_type):
        """Return all reftypes associated with processing all steps of all pipelines for `exp_type`."""
        # with log.error_on_exception("Failed exptype_to_reftypes for", srepr(exp_type)):
        reftypes = []
        for pipeline in self.exptype_to_pipelines(exp_type): 
            reftypes.extend(self.get_pipeline_types(pipeline, exp_type))
        reftypes = sorted(list(set(reftypes)))
        return reftypes
    
    def get_level_pipeline(self, level, exp_type):
        """Interpret the level_pipeline_exptypes data structure relative to
        processing `level` and `exp_type` to determine a pipeline .cfg file.
    
        Return [ pipeline .cfg ]  or  []
        """
        pipeline_exptypes = self.loaded_cfg.level_pipeline_exptypes[level]
        for mapping in pipeline_exptypes:
            for pipeline, exptypes in mapping.items():
                for exptype_pattern in exptypes:
                    if glob_match(exptype_pattern, exp_type):
                        return [pipeline]
        log.error("Unhandled EXP_TYPE", srepr(exp_type))
        return []
    
        # raise exceptions.CrdsPipelineCfgDeterminationError("Unhandled EXP_TYPE", srepr(exp_type))
    
    def get_pipeline_types(self, pipeline, exp_type):
        """Based on a pipeline .cfg filename and an EXP_TYPE,  look up
        the Steps corresponding to the .cfg and extrapolate those to the
        reftypes used by those Steps.   If there are exceptions to the
        reftypes assigned for a particular Step that depend on EXP_TYPE,
        return the revised types for that Step instead.
         
        Return [reftypes, ...]
        """
        steps = self.pipeline_cfgs_to_steps[pipeline]
        reftypes = []
        for step in steps:
            if step not in self.loaded_cfg.steps_to_reftypes_exceptions:
                reftypes.extend(self.steps_to_reftypes[step])
            else:
                for case in self.loaded_cfg.steps_to_reftypes_exceptions[step]:
                    item = list(case.values())[0]
                    more_reftypes = item["reftypes"][:]
                    exptypes = item["exp_types"][:]
                    found = False
                    for exptype_pattern in exptypes:
                        if glob_match(exptype_pattern, exp_type):
                            log.verbose("Adding exceptional types", more_reftypes, 
                                        "for step", srepr(step), "case", srepr(exptype_pattern), 
                                        "based on exp_type", srepr(exp_type))
                            found = True
                            reftypes.extend(more_reftypes)
                            break
                    if found:
                        break
                else:
                    raise exceptions.CrdsPipelineTypeDeterminationError("Unhandled EXP_TYPE for exceptional Step", srepr(step))
        return reftypes
    
# --------------------------------------------------------------------------------------

def glob_match(expr, value):
    """Convert the given glob `expr` to a regex and match it to `value`."""
    re_str = fnmatch.translate(expr)
    return re.match(re_str, value)

# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    with open(sys.argv[1]) as infile:
        print(CrdsCfgGenerator(infile.read()))

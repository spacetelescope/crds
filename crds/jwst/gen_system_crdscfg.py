from jwst.stpipe import cmdline
import yaml

'''
DARK, (LED, LAMP, FLAT)  all level2a only
DARK has special calwebb_dark

All otheres go through both level2a and level2b
'''

HEADER_YAML = """
author: CRDS
descrip: "Reference used to determine pipeline configuration from dataset parameters."
history: "First version generated from calcode .cfg files and EXP_TYPE/LEVEL mapping."
instrument: SYSTEM
pedigree: DUMMY
reftype: CRDSCFG
telescope: JWST
useafter: 1900-01-01T00:00:00
"""

# Input manually
# Order is important since the first pattern matching an exp_type in any given level wins.
PIPELINE_CFGS_YAML = """
pipeline_cfgs: [calwebb_dark.cfg, calwebb_sloper.cfg, calwebb_spec2.cfg, calniriss_soss2.cfg,
  calwebb_image2.cfg]
"""

# Input manually
LEVEL_PIPELINE_EXPTYPE_YAML = """
level_pipeline_exptypes:
    level2a:
        - calwebb_dark.cfg: [FGS_DARK, MIR_DARK, NRC_DARK, NIS_DARK, NRS_DARK]

        - calwebb_sloper.cfg: ["*"]

    level2b:
        - calwebb_spec2.cfg: [MIR_LRS-FIXEDSLIT, MIR_LRS-SLITLESS, MIR_MRS, NRS_FIXEDSLIT, 
                             NRS_MSASPEC, NRS_IFU, NRS_BRIGHTOBJ, NRS_AUTOWAVE]

        - calniriss_soss2.cfg: [NIS_SOSS]

        - calwebb_image2.cfg: [NRC_IMAGE, NRC_TACQ, NRC_CORON, NRC_FOCUS, 
                             MIR_IMAGE, MIR_TACQ, MIR_LYOT, MIR_4QPM, MIR_CORONCAL,
                             NIS_IMAGE, NIS_AMI, NIS_TACQ,
                             NRS_IMAGE, NRS_FOCUS, NRS_MIMF, NRS_BOTA, NRS_TACQ, NRS_TASLIT, NRS_TACONFIRM, NRS_CONFIRM,
                             FGS_IMAGE, FGS_FOCUS]

        - skip_2b.cfg: ["*DARK*", "*FLAT*", "*LED*", "*LAMP*", NIS_FOCUS, NIS_WFSS, NRS_AUTOWAVE]
"""

STEPS_TO_REFTYPE_EXCEPTIONS_YAML = """
steps_to_reftypes_exceptions:
    flat_field:
        - case1:
            exp_types: [NRS_FIXEDSLIT, NRS_IFU, NRS_MSASPEC]
            reftypes: [dflat, fflat, sflat]
        - case2:
            exp_types: ["NRS_*"]
            reftypes: []
        - case3:
            exp_types: ["*"]
            reftypes: [flat]
"""

# --------------------------------------------------------------------------------------

def generate_crdscfg_yaml():
    """Generate the SYSTEM CRDSCFG reference YAML."""
    pipeline_cfgs = yaml.load(PIPELINE_CFGS_YAML)["pipeline_cfgs"]
    pipeline_cfgs_to_steps, all_steps_to_reftypes = generate_pipeline_info(pipeline_cfgs)
    crdscfg = HEADER_YAML + PIPELINE_CFGS_YAML + LEVEL_PIPELINE_EXPTYPE_YAML + "\n"
    crdscfg += yaml.dump({"pipeline_cfgs_to_steps" : pipeline_cfgs_to_steps}) + "\n"
    crdscfg += yaml.dump({"steps_to_reftypes" : all_steps_to_reftypes})
    crdscfg += STEPS_TO_REFTYPE_EXCEPTIONS_YAML
    return crdscfg
    
def generate_pipeline_info(pipeline_cfgs):
    pipeline_cfgs_to_steps = {}
    all_steps_to_reftypes = {}
    pipeline_cfgs_to_steps["skip_2b.cfg"] = []
    for pipeline_cfg in pipeline_cfgs:
        steps_to_reftypes = cmdline.steps_to_reftypes_from_config(pipeline_cfg)
        pipeline_cfgs_to_steps[pipeline_cfg] = sorted(list(steps_to_reftypes.keys()))
        all_steps_to_reftypes.update(steps_to_reftypes)
    return pipeline_cfgs_to_steps, all_steps_to_reftypes

# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    print(generate_crdscfg_yaml())

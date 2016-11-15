"""This module provides functions that interface with the JWST calibration code to determine
things like "reference types used by a pipeline."
"""
import fnmatch
import re

import yaml

from crds import log

# from jwst.stpipe import cmdline

'''
I don’t think SDP has much in this area, but here is what is currently in place.  This is the .py code that selects the calibration recipe to apply at a designated calibration level, given a few keywords from the FITS header or Asn Table (EXP_TYPE is the main one, TEMPLATE and ASN_TYPE are also used).   This is the code that we talked about removing from SDP, and placing in a look-up file within CRDS so that the SSB would have full control over the mapping of instrument modes to recipes, since SSB writes the recipes, but I think that was pushed out to a future build.

Hope this helps.  Questions welcome,
Mike


    def apply_rules(self, recipe_header_keys):
        """Apply the calibration recipe selection rules to FITS keywords."""
        # set default
        calibration_recipe_name = 'UNKNOWN'

        # write some context msgs to a file in the local directory,
        #   in case debugging is needed for the recipe selection algorithm
        #   (they can't be logged because STDOUT is being used to
        #    send back the calibration recipe name, and they would
        #    intefere with that)
        fdmsg = open('get_calib_recipe.'+self.input_filename+"_log", 'w')
        fdmsg.write("calibration recipe calibration_level = " +
                     str(self.calibration_level) + "\n")
        fdmsg.write("recipe selection keyword values = " +
                     str(recipe_header_keys) + "\n")

        # level2a recipe selection
        if self.calibration_level == 'level2a':
            if recipe_header_keys['EXP_TYPE'][-4:] == 'DARK':
                calibration_recipe_name = 'calwebb_dark.cfg'
            else:
                calibration_recipe_name = 'calwebb_sloper.cfg'

        # level2b recipe selection
        elif self.calibration_level == 'level2b':

            # as of Build6 all spectroscopic modes map to the same recipe
            if (recipe_header_keys['EXP_TYPE'][:7] == 'MIR_LRS' or
                recipe_header_keys['EXP_TYPE'] == 'MIR_MRS' or
                recipe_header_keys['EXP_TYPE'] == 'NRS_FIXEDSLIT' or
                recipe_header_keys['EXP_TYPE'] == 'NRS_MSASPEC' or
                recipe_header_keys['EXP_TYPE'] == 'NRS_IFU'):
                calibration_recipe_name = 'calwebb_spec2.cfg'

            # FOR NOW, this one needs a custom recipe (accdg to Howard)
            #   but eventually will use calwebb_spec2
            elif recipe_header_keys['EXP_TYPE'] == 'NIS_SOSS':
                calibration_recipe_name = 'calniriss_soss2.cfg'

            # LOTS of imaging mode types (almost a default, but we probably
            #   don't want a default that will mask unsupported modes)
            #
            elif (recipe_header_keys['EXP_TYPE'] == 'NRC_IMAGE' or
                  recipe_header_keys['EXP_TYPE'] == 'NRC_TACQ' or
                  recipe_header_keys['EXP_TYPE'] == 'NRC_CORON' or
                  recipe_header_keys['EXP_TYPE'] == 'NRC_FOCUS' or
                  recipe_header_keys['EXP_TYPE'] == 'MIR_IMAGE' or
                  recipe_header_keys['EXP_TYPE'] == 'MIR_TACQ' or
                  recipe_header_keys['EXP_TYPE'] == 'MIR_LYOT' or
                  recipe_header_keys['EXP_TYPE'] == 'MIR_4QPM' or
                  recipe_header_keys['EXP_TYPE'] == 'MIR_CORONCAL' or
                  recipe_header_keys['EXP_TYPE'] == 'NIS_IMAGE' or
                  recipe_header_keys['EXP_TYPE'] == 'NIS_AMI' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_IMAGE' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_FOCUS' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_MIMF' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_BOTA' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_TACQ' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_TASLIT' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_TACONFIRM' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_CONFIRM' or
                  recipe_header_keys['EXP_TYPE'] == 'FGS_IMAGE' or
                  recipe_header_keys['EXP_TYPE'] == 'FGS_FOCUS' or
                  ( recipe_header_keys['EXP_TYPE'] == 'None' and
                    recipe_header_keys['TEMPLATE'] == 'FGS Imaging')):
                calibration_recipe_name = 'calwebb_image2.cfg'

            # These are meant to SKIP level-2b, so this recipe name can
            #   be trapped by the wrapper script, and used to exit without
            #   attempting calibration
            #
            elif (recipe_header_keys['EXP_TYPE'][-4:] == 'DARK' or
                  recipe_header_keys['EXP_TYPE'][-4:] == 'FLAT' or
                  recipe_header_keys['EXP_TYPE'] == 'MIR_FLATMRS' or
                  recipe_header_keys['EXP_TYPE'] == 'MIR_FLATIMAGE' or
                  recipe_header_keys['EXP_TYPE'] == 'NRC_LED' or
                  recipe_header_keys['EXP_TYPE'] == 'NIS_FOCUS' or
                  recipe_header_keys['EXP_TYPE'] == 'NIS_WFSS' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_AUTOWAVE' or
                  recipe_header_keys['EXP_TYPE'] == 'NRS_LAMP' or
                  recipe_header_keys['EXP_TYPE'] == 'NIS_LAMP'):
                calibration_recipe_name = 'SKIP_LEVEL_2B'
            else:
                # mode is not yet supported by calibration recipes
                print str(recipe_header_keys)
                fdmsg.write("recipe = UNSUPPORTED_CALIBRATION_MODE\n")
                fdmsg.close()
                raise UnsupportedCalibrationMode

        # level3 recipe selection (from parsing the Asn Table .json file)
        elif self.calibration_level == 'level3':
            # not many so far...
            if recipe_header_keys['ASN_TYPE'] == "WFS_Dither":
                calibration_recipe_name = 'wfs_combine.cfg'
            elif recipe_header_keys['ASN_TYPE'] == 'NIS_AMI':
                calibration_recipe_name = 'calniriss_ami3.cfg'
            else:
                # FOR NOW assume all other level3s fall through to this one
                # (though Howard points out this will fail big-time for
                #  spectroscopic modes)
                calibration_recipe_name = 'calwebb_image3.cfg'

        fdmsg.write("recipe = "+ calibration_recipe_name + "\n")
        fdmsg.close()
        return calibration_recipe_name
    # end apply_rules


    def find_recipe(self):
        """Look up the calibration recipe for given file and data level."""
        recipe_header_keys = {}
        if self.input_filename[-5:] == '.fits':
            # for FITS input, pull keywords from the input file,
            #    relevant for the data level,
            #    to determine which calibration recipe applies at that level
            hdulist = pyfits.open(self.input_filename)
            prihdr = hdulist[0].header
            for keyword in DATA_LEVEL_KEYWORD_MAPPING[self.calibration_level]:
                recipe_header_keys[keyword] = prihdr.get(keyword)
            hdulist.close()
        elif self.input_filename[-5:] == '.json':
            # for JSON input, grep values from the Asn Table input file,
            #    to determine which calibration recipe applies
            logname = '/tmp/get_calib_recipe_'+ self.input_filename
            # Bourne shell syntax, append stdout,stderr to separate logfiles
            cmd = '/bin/grep asn_rule {} 1>> {}.out 2>> {}.err'.format(
                   self.input_filename, logname, logname)
            #self.log.info("grep cmd: {}\n".format(cmd))
            retcode, dontcare_stdout_data_, dontcare_stderr_data_ = \
                                                            utils.run_cmd(cmd)
            if (retcode != 0):
                self.log.error("grep FAILED on {}, status={}".format(
                               self.input_filename, retcode))
                self.log.info("check log: {}".format(logname+".err"))
            else:
                # parse out the asn_rule from the output file
                # sampleline= {"asn_rule": "WFS_Dither",
                grepline = open(logname+'.out','r').readline()
                part_trim = grepline.split()[1][1:] # get 2nd "word", skip quote
                asn_type = part_trim[:-2] # trim ending quote+comma
                #self.log.info("asn_type={}".format(asn_type))
                recipe_header_keys['ASN_TYPE'] = asn_type
                # cleanup logs
                os.remove(logname+".err")
                os.remove(logname+".out")

        # determine the calibration recipe for the data level,
        #   based on the keyword values
        calibration_recipe_name = self.apply_rules(recipe_header_keys)

'''


PIPELINES = [
    "calwebb_dark.cfg",
    "calwebb_sloper.cfg",

    "calwebb_spec2.cfg",
    "calniriss_soss2.cfg",
    "calwebb_image2.cfg",
]

def print_types():
    from jwst.stpipe import cmdline
    for pipeline in PIPELINES:
        print(pipeline, "::", " ".join(cmdline.reference_types_from_config(pipeline)))


'''
DARK, (LED, LAMP, FLAT)  all level2a only
DARK has special calwebb_dark

All otheres go through both level2a and level2b
'''


CFGMAP_YAML = """
level2a:
        calwebb_dark.cfg: [FGS_DARK, MIR_DARK, NRC_DARK, NIS_DARK, NRS_DARK]
        calwebb_sloper.cfg: ["*"]

level2b:
        calwebb_spec2.cfg: [MIR_LRS-FIXEDSLIT, MIR_LRS-SLITLESS, MIR_MRS, NRS_FIXEDSLIT, NRS_MSASPEC, NRS_IFU]

        calniriss_soss2.cfg: [NIS_SOSS]

        calwebb_image2.cfg: [NRC_IMAGE, NRC_TACQ, NRC_CORN, NRC_FOCUS, 
                             MIR_IMAGE, MIR_TACQ, MIR_LYOT, MIR_4QPM, MIR_CORONCAL,
                             NIS_IMAGE, NIS_AMI, 
                             NRS_IMAGE, NRS_FOCUS, NRS_MIMF, NRS_BOTA, NRS_TACQ, NRS_TASLIT, NRS_TACONFIRM]

        skip_2b.cfg: ["*DARK*", "*FLAT*", "*LED*", "*WSS*", "*LAMP*", NIS_FOCUS, NIS_WFSS, NRS_AUTOWAVE]
"""

PIPELINE_TO_REFTYPES = {
    'calniriss_soss2.cfg': [
        'area',
        'camera',
        'collimator',
        'disperser',
        'distortion',
        'filteroffset',
        'fore',
        'fpa',
        'fringe',
        'ifufore',
        'ifupost',
        'ifuslicer',
        'msa',
        'ote',
        'photom',
        'regions',
        'specwcs',
        'straymask',
        'v2v3',
        'wavelengthrange',
        ],
    'calwebb_dark.cfg': [
        'ipc',
        'linearity',
        'mask',
        'refpix',
        'rscd',
        'saturation',
        'superbias',
        ],
    'calwebb_image2.cfg': [
        'area',
        'camera',
        'collimator',
        'disperser',
        'distortion',
        'filteroffset',
        'fore',
        'fpa',
        'ifufore',
        'ifupost',
        'ifuslicer',
        'msa',
        'ote',
        'photom',
        'regions',
        'specwcs',
        'v2v3',
        'wavelengthrange',
        ],
    'calwebb_sloper.cfg': [
        'dark',
        'gain',
        'ipc',
        'linearity',
        'mask',
        'readnoise',
        'refpix',
        'rscd',
        'saturation',
        'superbias',
        ],
    'calwebb_spec2.cfg': [
        'area',
        'camera',
        'collimator',
        'disperser',
        'distortion',
        'filteroffset',
        'fore',
        'fpa',
        'fringe',
        'ifufore',
        'ifupost',
        'ifuslicer',
        'msa',
        'ote',
        'photom',
        'regions',
        'specwcs',
        'straymask',
        'v2v3',
        'wavelengthrange',
        ],
 'skip_2b.cfg': []}

CFGMAP = {
    'level2a': {
        'calwebb_dark.cfg': [
            'FGS_DARK',
            'MIR_DARK',
            'NRC_DARK',
            'NIS_DARK',
            'NRS_DARK'
            ],
        'calwebb_sloper.cfg': [
            '*',
            ]
        },
    'level2b': {
        'calniriss_soss2.cfg': [
            'NIS_SOSS',
            ],
        'calwebb_image2.cfg': [
            'NRC_IMAGE',
            'NRC_TACQ',
            'NRC_CORN',
            'NRC_FOCUS',
            'MIR_IMAGE',
            'MIR_TACQ',
            'MIR_LYOT',
            'MIR_4QPM',
            'MIR_CORONCAL',
            'NIS_IMAGE',
            'NIS_AMI',
            'NRS_IMAGE',
            'NRS_FOCUS',
            'NRS_MIMF',
            'NRS_BOTA',
            'NRS_TACQ',
            'NRS_TASLIT',
            'NRS_TACONFIRM'
            ],
        'calwebb_spec2.cfg': [
            'MIR_LRS-FIXEDSLIT',
            'MIR_LRS-SLITLESS',
            'MIR_MRS',
            'NRS_FIXEDSLIT',
            'NRS_MSASPEC',
            'NRS_IFU',
            ],
        'skip_2b.cfg': [
            '*DARK*',
            '*FLAT*',
            '*LED*',
            '*WSS*',
            '*LAMP*',
            'NIS_FOCUS',
            'NIS_WFSS',
            'NRS_AUTOWAVE',
            ]
        }
    }

def get_pipeline_reftypes():
    """Return a global mapping from JWST cal code top level pipeline .cfg files
    to the reftypes required to process each sub-Step as a Python dict.
    """
    from jwst.stpipe import cmdline
    pipeline_to_reftypes = {}
    for pipeline in PIPELINES:
        pipeline_to_reftypes[pipeline] = cmdline.reference_types_from_config(pipeline)
    pipeline_to_reftypes["skip_2b.cfg"] = []
    # print(yaml.dump(pipeline_to_reftypes))
    return pipeline_to_reftypes

def header_to_reftypes(header):
    """Given a dataset `header`,  extract the EXP_TYPE or META.EXPOSURE.TYPE keyword
    from and use it to look up the reftypes required to process it.

    Return a list of reftype names.
    """
    with log.augment_exception("Can't find EXP_TYPE for:\n", log.PP(header)):
        exp_type = header.get("META.EXPOSURE.TYPE", header.get("EXP_TYPE"))
    return exptype_to_reftypes(exp_type)

def exptype_to_reftypes(exp_type):
    """For a given EXP_TYPE string, return a list of reftypes needed to process that
    EXP_TYPE through the data levels appropriate for that EXP_TYPE.

    Return [reftypes... ]
    """
    level_2a_types = get_level_reftypes(CFGMAP["level2a"], exp_type)
    level_2b_types = get_level_reftypes(CFGMAP["level2b"], exp_type)
    return level_2a_types + level_2b_types

def get_level_reftypes(pipelines, exp_type):
    """Given a dictionary `pipelines` mapping cal code .cfg files to EXP_TYPE
    glob patterns,  determine the pipeline .

    Return [reftypes... to process exp_type]
    """
    pipeline_cfg = get_level_pipeline(pipelines, exp_type)
    return PIPELINE_TO_REFTYPES[pipeline_cfg]

def get_level_pipeline(pipelines, exp_type):
    """Given a dictionary `pipelines` mapping cal code .cfg files to EXP_TYPE
    glob patterns,  determine the pipeline name for which some pattern matches.

    Return pipeline .cfg name
    """
    for pipeline in pipelines:
        for exp_type_expr in pipelines[pipeline]:
            if glob_match(exp_type_expr, exp_type):
                return pipeline
    raise RuntimeError("Unhandled EXP_TYPE " + repr(exp_type))

def glob_match(expr, value):
    """Convert the given glob `expr` to a regex and match it to `value`."""
    re_str = fnmatch.translate(expr)
    return re.match(re_str, value)

if __name__ == "__main__":
    print_types()


"""This module provides a project independent interface for determining the sequence of
pipelines used to process the given dataset filepath or dataset with a particular header.

>>> header_to_pipelines(test_header("0.7.0", "FGS_DARK"))
['calwebb_dark.cfg', 'skip_2b.cfg']

>>> header_to_pipelines(test_header("0.7.0", "NRS_BRIGHTOBJ"))
['calwebb_sloper.cfg', 'calwebb_spec2.cfg']

>>> header_to_pipelines(test_header("0.7.0", "MIR_IMAGE"))
['calwebb_sloper.cfg', 'calwebb_image2.cfg']

>>> header_to_pipelines(test_header("0.7.0", "MIR_LRS-FIXEDSLIT"))
['calwebb_sloper.cfg', 'calwebb_spec2.cfg']

"""
from crds.core import utils
from crds import data_file

# --------------------------------------------------------------------------------------

def test_header(calver, exp_type):
    """Create a header-like dict from `calver` and `exp_type` to support
    testing.
    """
    header = {
        "META.INSTRUMENT.NAME" : "SYSTEM",
        "REFTYPE" : "CRDSCFG",
        "META.CALIBRATION_SOFTWARE_VERSION" : calver,
        "META.EXPOSURE.TYPE" : exp_type,
        }
    return header

# --------------------------------------------------------------------------------------

def filepath_to_pipelines(dataset_path, context=None):
    """Given `dataset_path` and `context` name,  return the sequence of calibration
    code pipeline .cfg files nominally required to process `dataset_path`.
    """
    header = data_file.get_header(dataset_path, context)
    return header_to_pipelines(header, context)

def header_to_pipelines(header, context=None):
    """Based on `header` and `context` provide the project specific list of calibration
    code pipelines (.cfg files) used to process a dataset with `header`.
    """
    locator = utils.header_to_locator(header)
    return locator.header_to_pipelines(header, context)

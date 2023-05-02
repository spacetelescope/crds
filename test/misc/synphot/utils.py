import os

from crds.core import rmap
from crds import config
from crds.hst import locate


_COS_PARAMETRIZED_COMPONENTS = {
    "cosmcp_g130mc1055m", "cosmcp_g130mc1096m", "cosmcp_g130mc1222m",
    "cosmcp_g130mc1291m", "cosmcp_g130mc1300m", "cosmcp_g130mc1309m",
    "cosmcp_g130mc1318m", "cosmcp_g130mc1327m", "cosmcp_g140lc1230m",
    "cosmcp_g140lc1280m", "cosmcp_g160mc1577m", "cosmcp_g160mc1589m",
    "cosmcp_g140lc1105m", "cosmcp_g140lc800m", "cosmcp_g160mc1533m",
    "cosmcp_g160mc1600m", "cosmcp_g160mc1611m", "cosmcp_g160mc1623m",
    "cosncm3g185mc1786m", "cosncm3g185mc1817m", "cosncm3g185mc1835m",
    "cosncm3g185mc1850m", "cosncm3g185mc1864m", "cosncm3g185mc1882m",
    "cosncm3g185mc1890m", "cosncm3g185mc1900m", "cosncm3g185mc1913m",
    "cosncm3g185mc1921m", "cosncm3g185mc1941m", "cosncm3g185mc1953m",
    "cosncm3g185mc1971m", "cosncm3g185mc1986m", "cosncm3g185mc2010m",
    "cosncm3g225mc2186m", "cosncm3g225mc2217m", "cosncm3g225mc2233m",
    "cosncm3g225mc2250m", "cosncm3g225mc2268m", "cosncm3g225mc2283m",
    "cosncm3g225mc2306m", "cosncm3g225mc2325m", "cosncm3g225mc2339m",
    "cosncm3g225mc2357m", "cosncm3g225mc2373m", "cosncm3g225mc2390m",
    "cosncm3g225mc2410m", "cosncm3g230lc2635m", "cosncm3g230lc2950m",
    "cosncm3g230lc3000m", "cosncm3g230lc3360m", "cosncm3g230lc3360m",
    "cosncm3g285mc2617m", "cosncm3g285mc2637m", "cosncm3g285mc2657m",
    "cosncm3g285mc2676m", "cosncm3g285mc2695m", "cosncm3g285mc2709m",
    "cosncm3g285mc2719m", "cosncm3g285mc2739m", "cosncm3g285mc2850m",
    "cosncm3g285mc2952m", "cosncm3g285mc2979m", "cosncm3g285mc2996m",
    "cosncm3g285mc3018m", "cosncm3g285mc3035m", "cosncm3g285mc3057m",
    "cosncm3g285mc3074m", "cosncm3g285mc3094m",
}

_ACS_PARAMETRIZED_COMPONENTS = {
    "acs_fr388n", "acs_fr388n", "acs_fr423n",
    "acs_fr459m", "acs_fr462n", "acs_fr505n",
    "acs_fr551n", "acs_fr601n", "acs_fr647m",
    "acs_fr656n", "acs_fr716n", "acs_fr782n",
    "acs_fr853n", "acs_fr914m", "acs_fr1016n",
    "acs_fr931n",
}

_WFPC2_PARAMETRIZED_COMPONENTS = {
    "wfpc2_contpc1", "wfpc2_contwf2", "wfpc2_contwf3",
    "wfpc2_contwf4",
}

_MISC_PARAMETRIZED_COMPONENTS = {
    "wfpc_contpc": "pc_cont#",
    "wfpc_contwf": "wf_cont#",
    "wfpc2_lrf": "wave#",
}

_GRAPH_KEYWORD_OVERRIDES = {
    # This oddball keyword is technically a bug in the graph, but
    # code in stsynphot and seemingly also IRAF exists to compensate
    # for it.
    "wfpc2_lrf": "lrf#",
    # Here "cont#" is intended as a sort of alias for "pc_cont#" or
    # "wf_cont#", so the graph will have a different value from
    # the lookup table or the throughput file.
    "wfpc_contwf": "cont#",
    "wfpc_contpc": "cont#",
}

# wfpc2 must occur before wfpc in this list, so that prefix
# checks will assign the correct instrument:
_HST_INSTRUMENTS = [
    "acs", "cos", "stis", "wfc3", "wfpc2",
    "foc", "hrs", "hsp", "nicmos", "wfpc",
    "ota", "fgs", "fos"
]

_NICMOS_COMPONENT_PREFIXES = {
    "nic", "nic1", "nic2", "nic3"
}

_OTA_COMPONENTS = {
    "clear", "dark", "hst_ota"
}

_NON_HST_INSTRUMENT = "nonhst"

ALL_INSTRUMENTS = _HST_INSTRUMENTS + [_NON_HST_INSTRUMENT]

GRAPH_REFTYPE = "tmgtab"
THROUGHPUT_REFTYPE = "thruput"
THROUGHPUT_LOOKUP_REFTYPE = "tmctab"
THROUGHPUT_FILENAME_SUFFIX = "syn"
THERMAL_REFTYPE = "thermal"
THERMAL_LOOKUP_REFTYPE = "tmttab"
THERMAL_FILENAME_SUFFIX = "th"
OBSMODES_REFTYPE = "obsmodes"
SYNPHOT_INSTRUMENT = "synphot"

# These are thermal components that are present in the lookup
# table but missing from the graph and individual component file
# headers. We can get rid of this once
# https://jira.stsci.edu/browse/REDCAT-100 is resolved.
KNOWN_MISSING_GRAPH_THERMAL_COMPONENTS = {
    "wfc3_ir_cor",
    "wfc3_ir_dn",
}

# These are thermal components that are present in the graph
# table but missing from the thermal lookup and individual component
# file headers.  We can get rid of this once
# https://jira.stsci.edu/browse/REDCAT-104 is resolved.
KNOWN_MISSING_THERMAL_LOOKUP_COMPONENTS = {
    "clear",
    "dark",
    "nic1_dn",
    "nic2_dn",
    "nic3_dn",
}

# These are throughput components that are present in the graph
# and lookup tables but missing from the individual file headers.
# We can get rid of this once
# https://jira.stsci.edu/browse/REDCAT-102 is resolved.
KNOWN_MISSING_THROUGHPUT_COMPONENTS = {
    "nic1_primary",
    "nic1_sec",
    "nic2_primary",
    "nic2_sec",
    "nic3_primary",
    "nic3_sec",
}

# These are thermal components that are present in the graph
# and lookup tables but missing from the individual file headers.
# We can get rid of this once
# https://jira.stsci.edu/browse/REDCAT-103 is resolved.
KNOWN_MISSING_THERMAL_COMPONENTS = {
    "nic1_bend", "nic1_bend1", "nic1_cmask", "nic1_dewar", "nic1_edge",
    "nic1_hole", "nic1_image", "nic1_pads", "nic1_para1", "nic1_para2",
    "nic1_primary", "nic1_pupil", "nic1_reimag", "nic1_sec", "nic1_spider",
    "nic2_sec", "nic3_bend", "nic3_bend1", "nic3_cmask", "nic3_dewar",
    "nic3_edge", "nic3_hole", "nic3_image", "nic3_pads", "nic3_para1",
    "nic3_para2", "nic3_primary", "nic3_pupil", "nic3_reimag", "nic3_sec",
    "nic3_spider"
}


def make_filename(reftype):
    """
    Create a unique name for the specified synphot graph or lookup reftype.
    """
    return locate.generate_unique_name_core(SYNPHOT_INSTRUMENT, reftype, ".fits")


def get_cache_path(context, reftype, error_on_missing=True):
    """
    Fetch the full path to the single reference file of reftype.
    """
    context = rmap.asmapping(context)
    imap = context.get_imap(SYNPHOT_INSTRUMENT)
    mapping = imap.get_rmap(reftype)
    filenames = mapping.reference_names()

    if len(filenames) == 0 and not error_on_missing:
        return None

    if len(filenames) != 1:
        raise RuntimeError("Expected '{}' rmap to contain one reference file".format(reftype))

    filename = filenames[0]
    return config.locate_file(filename, observatory="hst")


def get_instrument(component):
    """
    Get the *synphot* instrument corresponding to component.  Note that this
    is a superset of the CRDS HST instruments.
    """
    component = component.lower()

    for instrument in _HST_INSTRUMENTS:
        if component.startswith(instrument):
            return instrument

    if any(component.startswith(p) for p in _NICMOS_COMPONENT_PREFIXES):
        return "nicmos"

    if component in _OTA_COMPONENTS:
        return "ota"

    return _NON_HST_INSTRUMENT


def get_path_prefix(component):
    """
    Get the IRAF path prefix for the specified component.
    """
    instrument = get_instrument(component)
    return "cr{}comp$".format(instrument)


def get_lookup_filename(component, filename):
    """
    Get the lookup table filename for the specified component, which includes
    the IRAF path prefix and (if applicable) parametrized keyword suffix.
    """
    lookup_filename = get_path_prefix(component) + filename
    param_keyword = get_parametrization_keyword(component)
    if param_keyword is not None:
        lookup_filename = lookup_filename + "[{}]".format(param_keyword)
    return lookup_filename


def lookup_filename_to_path(synphot_root, lookup_filename):
    """
    Translate a filename from a lookup table into a full
    filesystem path.
    """
    prefix, other = lookup_filename.split("$")
    filename = other.split("[")[0]
    return os.path.join(synphot_root, "comp", prefix[2:-4], filename)


def get_mtab_path(synphot_root):
    """
    Get the full path to the synphot mtab directory.
    """
    return os.path.join(synphot_root, "mtab")


def get_instrument_path(synphot_root, instrument):
    """
    Get the full path to the synphot instrument's component directory.
    """
    return os.path.join(synphot_root, "comp", instrument)


def get_parametrization_keyword(component, is_graph=False):
    """
    Get the keyword prefix for a parametrized synphot component,
    or None if the component is not parametrized.
    """
    # Some of the individual files have uppercase COMPNAME, and there
    # are too many of them to be worth fixing.
    component = component.lower()

    if is_graph and component in _GRAPH_KEYWORD_OVERRIDES:
        return _GRAPH_KEYWORD_OVERRIDES[component]

    if component.endswith("_mjd") or component.endswith("_m"):
        return "mjd#"

    if component.endswith("_aper"):
        return "aper#"

    if component in _ACS_PARAMETRIZED_COMPONENTS:
        return component.split("_")[-1] + "#"

    if component in _COS_PARAMETRIZED_COMPONENTS:
        return "mjd#"

    if component in _WFPC2_PARAMETRIZED_COMPONENTS:
        return "cont#"

    if component in _MISC_PARAMETRIZED_COMPONENTS:
        return _MISC_PARAMETRIZED_COMPONENTS[component]

    return None

"""This module defines replacement functionality for the CDBS "certify" program which
is used to check parameter values in .fits reference files and .lod files.  certify.py
loads expressions of legal values from CDBS .tpn files and applies them to reference
files to look for discrepancies.
"""
import sys

import pyfits 

import crds.hst.tpn as tpn

from crds import rmap, log

def rmap_to_tpn(context, rmap_name):
    rmap_ = rmap.get_cached_mapping(rmap_name)
    return tpn.get_tpn(rmap_.instrument, rmap_.reftype)

INSTRUMENTS = ["acs","cos","stis","wfc3"]

def get_filetype_map(context):
    pipeline = rmap.get_cached_mapping(context)
    map = {}
    for instr in INSTRUMENTS:
        map[instr] = {}
    for i, name in enumerate(pipeline.reference_names()):
        ext = name.split("_")[1].split(".")[0].lower()
        hst = rmap.get_cached_mapping("hst.pmap")
        print "Scanning", i, name
        try:
            where = hst.locate.locate_server_reference(name)
        except KeyError:
            log.error("Missing reference file", repr(name))
            continue
        try:
            header = pyfits.getheader(where)
            filetype = header["FILETYPE"].lower()
            instrument = header["INSTRUME"].lower()
        except IOError, e: 
            log.error("Error getting FILETYPE for", repr(where))
        current = map.get(filetype, None)
        if current and current != ext:
            log.error("Multiple extensions for", repr(filetype), repr(current), repr(ext))
            continue
        if filetype not in map[instrument]:
            map[instrument][filetype] = ext
            log.info("Setting",repr(instrument), repr(filetype),"to extension",repr(ext))
    return map

# FILETYPE_TO_EXT = get_filetype_map("hst.pmap")

FILETYPE_TO_EXTENSION = {
 'acs': {'analog-to-digital': 'a2d',
         'bad pixels': 'bpx',
         'bias': 'bia',
         'ccd parameters': 'ccd',
         'cosmic ray rejection': 'crr',
         'dark': 'drk',
         'distortion coefficients': 'idc',
         'distortion correction': 'dxy',
         'linearity': 'lin',
         'multidrizzle parameters': 'mdz',
         'overscan': 'osc',
         'pixel-to-pixel flat': 'pfl',
         'spot flat': 'cfl',
         'spot position table': 'csp'},
 'cos': {'1-d extraction parameters table': '1dx',
         'bad time intervals table': 'badt',
         'baseline reference frame table': 'brf',
         'burst parameters table': 'burst',
         'data quality initialization table': 'bpix',
         'deadtime reference table': 'dead',
         'dispersion relation reference table': 'disp',
         'flat field reference image': 'flat',
         'geometric distortion reference image': 'geo',
         'photometric sensitivity reference table': 'phot',
         'pulse height parameters reference table': 'pha',
         'template cal lamp spectra table': 'lamp',
         'time dependent sensitivity table': 'tds',
         'wavecal parameters reference table': 'wcp'},
 'stis': {'1-d extraction parameter table': '1dx',
          '1-d spectrum trace table': '1dt',
          '2-d spectrum distortion correction table': 'sdc',
          'aperture description table': 'apd',
          'aperture throughput table': 'apt',
          'bad pixel table': 'bpx',
          'ccd bias image': 'bia',
          'ccd parameters table': 'ccd',
          'cosmic ray rejection table': 'crr',
          'cross-disperser scattering table': 'cds',
          'dark correction table': 'tdc',
          'dark image': 'drk',
          'detector halo table': 'hal',
          'dispersion coefficients table': 'dsp',
          'echelle cross-dispersion scattering table': 'exs',
          'echelle ripple table': 'rip',
          'image distortion correction table': 'idc',
          'incidence angle correction table': 'iac',
          'low-order flatfield image': 'lfl',
          'mama linearity table': 'lin',
          'mama offset correction table': 'moc',
          'photometric correction table': 'pct',
          'pixel-to-pixel flatfield image': 'pfl',
          'scattering reference wavelengths table': 'srw',
          'template cal lamp spectra table': 'lmp',
          'time dependent sensitivity table': 'tds',
          'wavecal parameters table': 'wcp'},
 'wfc3': {'bad pixels': 'bpx',
          'bias': 'bia',
          'ccd parameters': 'ccd',
          'cosmic ray rejection': 'crr',
          'dark': 'drk',
          'distortion coefficients': 'idc',
          'linearity coefficients': 'lin',
          'multidrizzle parameters': 'mdz',
          'overscan': 'osc',
          'pixel-to-pixel flat': 'pfl'}
}

class MissingKeywordError(Exception):
    """Reference file is missing a required keyword."""

def certify(fitsname):
    """Given reference filepath `fitsname`,  load the appropriate TPN and validate all
    of the header keywords listed in it.
    """
    header = pyfits.getheader(fitsname)
    instrument = header["INSTRUME"].lower()
    filetype = header["FILETYPE"].lower()
    extension = FILETYPE_TO_EXTENSION[instrument][filetype]
    the_tpn = tpn.get_tpn(instrument, extension)
    for keyname, validator in the_tpn.items():
        validator.check(fitsname, keyname, header)

def main(files):
    """Run certify() on a list of `files` logging an error for the first failure
    in each file,  but continuing.
    """
    for fname in files:
        log.info("Certifying", repr(fname))
        try:
            certify(fname)
        except Exception:
            raise
            log.error("Validation failed for", repr(fname))
    log.standard_status()
    
def reference_files(context):
    """Returns the list of server reference file paths for `context`"""
    ctx = rmap.get_cached_mapping(context)
    paths = []
    for ref in ctx.reference_names():
        try:
            paths.append(ctx.locate.locate_server_reference(ref))
        except KeyError:
            log.warning("Missing reference file", repr(ref))
    return paths

if __name__ == "__main__":
    main(sys.argv[1:])


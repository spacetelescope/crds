"""This module generates rmaps from pre-cloned (or complete) references and an rmap stub."""

import sys
import os.path

import pyfits

from crds import rmap, timestamp, pysh, log, data_file

RMAP_STUB = """
header = {
    'derived_from' : 'cloning tool 0.05b (2013-04-12) used on 2013-09-04',
    'filekind' : 'PHOTOM',
    'instrument' : 'MIRI',
    'mapping' : 'REFERENCE',
    'name' : 'jwst_miri_photom_0001.rmap',
    'observatory' : 'JWST',
    'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.FILTER'),),
    'sha1sum' : 'c36e180a97d16ff6a587500cdaaf85325442c080',
}

selector = Match({
})
"""

def generate_new_rmap(reference_context, parkey, new_references):
    """Create an entirely .rmap given a reference context and a list of new files
    of the same type.
    """
    log.info("context:", reference_context, "parkey:", parkey, "references:", new_references)

    pmap = rmap.get_cached_mapping(reference_context)

    old_instrument, old_filekind = None, None
    for ref in new_references:
        instrument, filekind = pmap.locate.get_file_properties(ref)
        assert not old_instrument or instrument == old_instrument, "Multiple instruments deteted at " + repr(ref)
        assert not old_filekind or filekind == old_filekind, "Multiple filekinds detected at " + repr(ref)
        old_instrument, old_filekind = instrument, filekind
        
        header = pyfits.getheader(ref)
        assert header["REFTYPE"] ==  pmap.locate.filekind_to_reftype(filekind)
        assert header["FILETYPE"] == pmap.locate.filekind_to_reftype(filekind)

    assert instrument in pmap.obs_package.INSTRUMENTS, "Invalid instrument " + repr(instrument)
    assert filekind in pmap.obs_package.FILEKINDS, "Invalid filekind at " + repr(filekind)

    name = "_".join(["jwst",instrument,filekind,"0000"]) + ".rmap"
    path = rmap.locate_mapping(name)
    
    new_rmap = rmap.ReferenceMapping.from_string(RMAP_STUB, name, ignore_checksum=True)
    new_rmap.header["instrument"] = instrument.upper()
    new_rmap.header["filekind"] = filekind.upper()
    new_rmap.header["parkey"] = eval(parkey.upper())
    new_rmap.header["name"] = name
    new_rmap.header["observatory"] = pmap.observatory.upper()
    
    new_rmap.write(path)
    
    files = " ".join(["./" + ref for ref in new_references])

    pysh.sh("python -m crds.refactor insert ${path} ${path} ${files} --verbose", 
            trace_commands=True, raise_on_error=True)
    
    new_rmap = rmap.load_mapping(path)
    new_rmap.validate_mapping()
    new_rmap.header["derived_from"] = 'generated as stub rmap on ' + timestamp.now()
    new_rmap.write(path)
    new_rmap = rmap.load_mapping(path)
    new_rmap.validate_mapping()
    
    return path

def generate_rmaps_and_context(reference_context, parkey, all_references):
    """Generate rmaps for complete (non-stub) references in `all_references` and then
    generate a higher level context derived from `reference_context` by inserting the
    new .rmaps.
    """
    pmap = rmap.get_cached_mapping(reference_context)
    rmaps = []
    for instr in pmap.obs_package.INSTRUMENTS:
        added_references = [ref for ref in all_references if instr.lower() in ref]
        path = generate_new_rmap(reference_context, parkey, added_references)
        rmaps.append(path)
        pysh.sh("cp $path .", trace_commands=True, raise_on_error=True)
    
    rmaps_str = " ".join([os.path.basename(mapping) for mapping in rmaps])
    pysh.sh("python -m crds.newcontext ${reference_context} ${rmaps_str} --verbose", trace_commands=True, raise_on_error=True)

if __name__ == "__main__":
        
    pysh.usage("<reference_context> <comma-separated-parkeys> <new_references>", 3)
    
    reference_context = sys.argv[1]
    parkey = sys.argv[2]
    all_references = sys.argv[3:]
    
    generate_rmaps_and_context(reference_context, parkey, all_references)


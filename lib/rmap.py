"""This module supports loading all the data components required to make
a CRDS lookup table for an instrument.
"""
import os
import os.path
import collections

from crds import log, timestamp
from crds.config import CRDS_ROOT

# ===================================================================

Filetype = collections.namedtuple("Filetype","header_keyword,extension,rmap")
Failure = collections.namedtuple("Failure","header_keyword,message")

# ===================================================================

class RmapError(Exception):
    """Exception in load_rmap."""
    def __init__(self, *args):
        Exception.__init__(self, " ".join([str(x) for x in args]))

# ===================================================================

class Rmap(object):
    def __init__(self, filename, header, data):
        self.filename = filename
        self.header = header
        self.data = data
    
    @classmethod
    def from_file(klass, fname, *args, **keys):
        try:
            namespace = {}
            execfile(fname, namespace, namespace)
        except:
            raise RmapError("Can't load", klass.__name__, "file:", repr(fname))
        try:
            header = namespace["header"]
        except:
            raise RmapError("Can't find 'header' in", klass.__name__, "file:", repr(fname))
        try:
            data = namespace["data"]
        except:
            raise RmapError("Can't find 'data' in", klass.__name__, "file:", repr(fname))
        rmap = klass(fname, header, data, *args, **keys)
        rmap.validate_file_load()
        return rmap
    
    def validate_file_load(self):
        pass
    
# ===================================================================

"""
header = {
    'observatory':'HST',
    'parkey' : ('INSTRUME'),
    'class' : 'crds.PipelineContext',
}

data = {
    'ACS':'icontext_hst_acs_00023.con',
    'COS':'icontext_hst_cos_00023.con', 
    'STIS':'icontext_hst_stis_00023.con',
    'WFC3':'icontext_hst_wfc3_00023.con',
    'NICMOS':'icontext_hst_nicmos_00023.con',
}
"""
class PipelineContext(Rmap):
    def __init__(self, filename, header, data, observatory):
        Rmap.__init__(self, filename, header, data)
        self.observatory = observatory.lower()
        self.selections = {}
        for instrument, context_file in data.items():
            instrument = instrument.lower()
            filepath = "/".join([CRDS_ROOT, self.observatory, instrument, context_file])
            self.selections[instrument] = InstrumentContext.from_file(filepath, observatory, instrument)
        
    def get_best_refs(self, header, date=None):
        header = dict(header.items())
        instrument = header["INSTRUME"].lower()
        if date == "now":
            date = timestamp.now()
        if date:
            header["DATE"] = date
        else:
            header["DATE"] = header["DATE-OBS"] + " " + header["TIME-OBS"]
        header["DATE"] = timestamp.reformat_date(header["DATE"])
        return self.selections[instrument].get_best_refs(header)
    
    def reference_files(self):
        """Return the list of reference files associated with this pipeline context."""
        files = set()
        for instrument in self.selections:
            for file in self.selections[instrument].reference_files():
                files.add(file)
        return sorted(list(files))
                
# ===================================================================

"""
header = {
    'observatory':'HST',
    'instrument': 'ACS',
    'parkey' : ('REFTYPE',),
    'class' : 'crds.InstrumentContext',
}

data = {
    'BIAS':  'rmap_hst_acs_bias_0021.rmap',
    'CRREJ': 'rmap_hst_acs_crrej_0003.rmap',
    'CCD':   'rmap_hst_acs_ccd_0002.rmap',
    'IDC':   'rmap_hst_acs_idc_0005.rmap',
    'LIN':   'rmap_hst_acs_lin_0002.rmap',
    'DISTXY':'rmap_hst_acs_distxy_0004.rmap',
    'BPIX':  'rmap_hst_acs_bpic_0056.rmap',
    'MDRIZ': 'rmap_hst_acs_mdriz_0001.rmap',
    ...
}
"""

class InstrumentContext(Rmap):
    def __init__(self, filename, header, data, observatory, instrument):
        Rmap.__init__(self, filename, header, data)
        self.observatory = observatory.lower()
        self.instrument = instrument.lower()
        self._selectors = {}
        for reftype, rmap_info in data.items():
            rmap_ext, rmap_name = rmap_info
            filepath = "/".join([CRDS_ROOT, self.observatory, self.instrument, rmap_name])
            self._selectors[reftype] = ReferenceRmap.from_file(
                filepath, self.observatory, self.instrument, reftype)

    def get_best_ref(self, reftype, header):
        return self._selectors[reftype.lower()].get_best_ref(header)

    def get_best_refs(self, header):
        refs = {}
        for reftype in self._selectors:
            log.verbose("\nGetting bestref for", repr(reftype))
            try:
                refs[reftype] = self.get_best_ref(reftype, header)
            except Exception, e:
                refs[reftype] = "NOT FOUND " + str(e)
        return refs

    def get_binding(self, header):
        """Given a header,  return the binding of all keywords pertinent to all reftypes
        for this instrument.
        """
        binding = {}
        for reftype in self._selectors:
            binding.update(self._selectors[reftype].get_binding(header))
        return binding
    
    def reference_files(self):
        files = set()
        for selector in self._selectors.values():
            for file in selector.reference_files():
                files.add(file)
        return sorted(list(files))

# ===================================================================

class ReferenceRmap(Rmap):
    """ReferenceRmap manages loading the rmap associated with a single reference
    filetype and instantiating an appropriate selector from the rmap header and data.
    """
    def __init__(self, filename, header, data, observatory, instrument, reftype):
        Rmap.__init__(self, filename, header, data)
        self.instrument = instrument.lower()
        self.observatory = observatory.lower()
        self.reftype = reftype.lower()
        klass = get_class(header.get("class", "crds.selectors.ReferenceSelector"))
        self._selector = klass(header, data)

    def validate_file_load(self):
        got = self.header["reftype"].lower()
        if got != self.reftype:
            raise RmapError("Expected reftype=" + repr(self.reftype), "but got reftype=", repr(got))

    def get_best_ref(self, header):
        return self._selector.choose(header)
    
    def reference_files(self):
        return self._selector.reference_files()
    
# ===================================================================

def get_class(dotted_name):
    """Import the given `dotted_name` and return the module object."""
    parts = dotted_name.split(".")
    pkgpath = ".".join(parts[:-1])
    klass = parts[-1]
    namespace = {}
    exec "from " + pkgpath + " import " + klass in namespace, namespace
    return namespace[klass]


# ===================================================================

PIPELINE_CONTEXTS = {}

def get_pipeline_context(observatory, context_file):
    observatory = observatory.lower()
    key = (observatory, context_file)
    if key in PIPELINE_CONTEXTS:
        return PIPELINE_CONTEXTS[key]
    filepath = "/".join([CRDS_ROOT, observatory, context_file])
    PIPELINE_CONTEXTS[key] = PipelineContext.from_file(filepath, observatory)
    return PIPELINE_CONTEXTS[key]

# ===================================================================

def get_best_refs(header, observatory="hst", pcontext_file=None, date=None):
    if pcontext_file is None:
        pcontext_file = observatory + ".pmap"
    context = get_pipeline_context(observatory, pcontext_file)
    return context.get_best_refs(header, date)

# ===================================================================

def test():
    """Run module doctests."""
    import doctest, rmap
    return doctest.testmod(rmap)

if __name__ == "__main__":
    print test()


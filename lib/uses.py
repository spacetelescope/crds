"""uses.py defines functions which will list the files which use a given reference
or mapping file.

>>> findall_mappings_using_reference("u451251ej_bpx.fits")
['hst.pmap', 'hst_acs.imap', 'hst_acs_bpixtab.rmap']

"""
import sys
import os.path

import crds.utils as utils
import crds.pysh as pysh

def findall_rmaps_using_reference(filename, observatory="hst"):
    """Return the basename of all reference mappings which mention 
    `filename`.
    """
    mapping_path = utils.get_crds_mappath(observatory)
    rmaps = pysh.lines("find ${mapping_path} -name '*.rmap' |"
                       " xargs grep -l ${filename}")
    return [os.path.basename(rmap.strip()) for rmap in rmaps]

def findall_imaps_using_rmap(filename, observatory="hst"):
    """Return the basenames of all instrument contexts which mention 
    `filename`.
    """
    mapping_path = utils.get_crds_mappath(observatory)
    imaps = pysh.lines("find ${mapping_path} -name '*.imap' |"
                       " xargs grep -l ${filename}")
    return [os.path.basename(imap.strip()) for imap in imaps]

def findall_pmaps_using_imap(filename, observatory="hst"):
    """Return the basenames of all pipeline contexts which mention 
    `filename`.
    """
    mapping_path = utils.get_crds_mappath(observatory)
    pmaps = pysh.lines("find ${mapping_path} -name '*.pmap' |"
                       " xargs grep -l ${filename}")
    return [os.path.basename(pmap.strip()) for pmap in pmaps]

def findall_mappings_using_reference(reference, observatory="hst"):
    """Return the basenames of all mapping files in the hierarchy which
    mentions reference `reference`.
    """
    mappings = []
    for rmap in findall_rmaps_using_reference(reference, observatory):
        mappings.append(rmap)
        for imap in findall_imaps_using_rmap(rmap, observatory):
            mappings.append(imap)
            for pmap in findall_pmaps_using_imap(imap, observatory):
                mappings.append(pmap)
    return sorted(list(set(mappings)))

def findall_mappings_using_rmap(rmap, observatory="hst"):
    """Return the basenames of all mapping files in the hierarchy which
    mentions reference mapping `rmap`.
    """
    mappings = []
    for imap in findall_imaps_using_rmap(rmap, observatory):
        mappings.append(imap)
        for pmap in findall_pmaps_using_imap(imap, observatory):
            mappings.append(pmap)
    return sorted(list(set(mappings)))

def test():
    """Run the module doctest."""
    import doctest, uses
    return doctest.testmod(uses)

def uses(files, observatory="hst"):
    """Return the list of mappings which use any of `files`.
    """
    mappings = []
    for file_ in files:
        if file_.endswith(".fits"):
            mappings.extend(
                findall_mappings_using_reference(file_, observatory))
        elif file_.endswith(".rmap"):
            mappings.extend(
                findall_mappings_using_rmap(file_, observatory))
        elif file_.endswith(".imap"):
            mappings.extend(
                findall_pmaps_using_imap(file_, observatory))
    return sorted(list(set(mappings)))

def main(observatory, files):
    """Print the "anscestor" mappings which mention each reference file,
    rmap, or imap in `files`.
    """
    mappings = uses(files, observatory)
    for mapping in mappings:
        print mapping

if __name__ == "__main__":
    main(observatory, sys.argv[2:])
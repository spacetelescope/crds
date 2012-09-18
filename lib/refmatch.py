import re

import pyfits
from . import rmap
from crds import client

filekind_kw = 'FILETYPE'

def get_filekind_vals(imap):
    """ Return the filekind values for all reference file types for this instrument
    """
    fkinds = {}
    instrume = imap.header['instrument'].lower()
    for ftype in imap.get_filekinds():
        fkind = None  # Initialize
        tpninfos = imap.locate.get_tpninfos(instrume, ftype.lower())
        for info in tpninfos:
            if info.name == filekind_kw:
                fkind = info.values[0]
                fkind = fkind.replace('"','') # Remove extra quotes
                break
        if fkind:
            fkinds[ftype] = fkind

    return fkinds

def determine_filekind(reffile,imap):
    """ Return the name of the reference file kind from the mapping file
        that corresponds to the file kind of the new reffile input.
    """
    newkind = pyfits.getval(reffile,filekind_kw)
    newkind = newkind.replace(' ','_') # get kw value into same format as tpninfo
    filetype = None # return value
    filekinds = get_filekind_vals(imap)
    for fkind in filekinds:
        if newkind in filekinds[fkind]:
            filetype = fkind
            break
    return filetype

def split_useafter(useafter, default_time='00:00:00'):
    """ Split the USEAFTER value from a reference file into a DATE and TIME
        value appropriate for ref file selection.

    >>> split_useafter("Jun 21 2011 21:00:00")
    ('Jun 21 2011 ', '21:00:00')

    >>> split_useafter("Jun 21 2011")
    ('Jun 21 2011', '00:00:00')

    >>> split_useafter('Apr 1 2000 12:00:00 pm')
    ('Apr 1 2000 ', '12:00:00')
    """
    if ':' in useafter:
        t = re.search('\d\d:\d\d:\d\d',useafter).group()
        d = useafter[:useafter.find(t)]
    else:
        d = useafter
        t = default_time
    return d,t

def find_current_reffile(reffile,pmap):
    """ Returns the name of the current reference file(s)
        that the new reffile would replace.
    """
    ctx = rmap.get_cached_mapping(pmap)
    instr = ctx.get_instrument(pyfits.getheader(reffile))
    i = ctx.get_imap(instr)

    filetype = pyfits.getval(reffile,filekind_kw)
    dateobs,timeobs = split_useafter(pyfits.getval(reffile,'USEAFTER'))

    filekind = determine_filekind(reffile, i)
    if filekind:
        r = i.get_rmap(filekind)
    else:
        print 'No valid reference file type found for filetype = ',filetype
        return None
    # Get selector kws from reffile to use to select current best matched reffile
    select_kws = r.get_required_parkeys()
    select_vals = {}
    for kw in select_kws:
        if kw == 'DATE-OBS':
            select_vals[kw] = dateobs
        elif kw == 'TIME-OBS':
            select_vals[kw] = timeobs
        else:
            select_vals[kw] = pyfits.getval(reffile,kw)
    match_refname = r.selector.choose(select_vals)
    # grab match_file from server and copy it to a local disk, if network
    # connection is available and configured properly
    # Note: this call works in both networked and non-networked modes of operation.
    # Non-networked mode requires access to /grp/crds/[hst|jwst] or a copy of it.
    try:
        match_files = client.dump_references(pmap, baserefs=[match_refname], ignore_cache=False)
        match_file = match_files[match_refname]
    except Exception:
        log.warning("Failed to obtain reference comparison file", repr(match_refname))
        match_file = None

    return match_file

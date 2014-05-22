"""This module encapsulates code related to determining the datasets which are affected
by table changes.   The nature of the optimization is that,  viewed as a file change,  CRDS
would think a new table "affects everything" and be forced to recommend reprocessing all datasets.
The code in this module is tasked with determining if the rows selected from two versions of
a table by particular dataset parameters are actually different.   

If the rows are not different, then effectifvely the new version of the table should not cause 
a dataset to be processed.

If the rows are different,  then the dataset should be reprocessed.  
"""

from crds import rmap

def is_reprocessing_required(dataset,  dataset_parameters, old_context, new_context, old_reference, new_reference):
    """This is the top level interface to crds.bestrefs running in "Affected Datasets" mode.
    
    It determines if reprocessing `dataset` with parameters `dataset_parameters` should be performed as
    a consequence of switching from `old_reference` to `new_reference`.  old_reference is assigned to dataset
    by old_context,  and new_reference is assigned to dataset by new_context.
        
    dataset              id of dataset being reprocessed,  <assoc>:<member> or <unassoc>:<unassoc> format
    
    dataset_parameters   { parameter : value, ...} for all matching parameters and row selection parameters
    
                        XXX row selection parameters not used in file selection may not be present until
                        XXX explicitly added to the CRDS interface to the DADSOPS parameter database...
                        XXX and possibly even to DADSOPS itself. Normally the row selections have only been
                        XXX done with direct access to dataset .fits files.
    
    old_context         loaded pmap or name of old context,  possibly for metadata or None

    new_context         loaded pmap or name of new context,  possibly for metadata
    
    old_reference       name or absolute path of old reference,  possibly not a table or None
    
    new_reference       name or absolute path of new reference,  possibly not a table
    
    Returns True        IFF reprocessing should be done as a consequence of the table change.
    """

    # Although the basic premise of the module is a table-based optimization,  if it could be
    # done for other references with benefit,  we'd want to rename the module and do it.   
    # So conceptually and practically,  these are references,  not necessarily tables.   
    # If non-tables are not  optimized,  that should be detected here and non-table-references 
    # reduced to True:  reprocess.
    
    # no old_context means "single context" mode,  always reprocess.
    if old_context == None:   
        return True
    
    # reprocess on transition from meaningless assignment (no comparison possible) to defined reference
    meaningless = ("n/a", "undefined", "not found",)
    if (old_reference.lower().startswith(meaningless) and 
        not new_reference.lower().startswith(meaningless)):
        return True

    # mostly debug wrappers here,  allows simple string parameters to work and resolves cache paths.
    old_context = rmap.asmapping(old_context, cached=True)   
    new_context = rmap.asmapping(new_context, cached=True)   
    old_reference = old_context.locate_file(old_reference)
    new_reference = new_context.locate_file(new_reference)

    # Return True *here* for non-tables,  needs to be fast,  no pyfits.
    # if not is_table(old_context, old_reference):
    #    return True
    
    # Return True *here* since there is no table code yet.
    return False


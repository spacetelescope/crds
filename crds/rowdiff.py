"""RowDiff: Produce diff-similar results between table extensions of two
FITS files or HDU lists. This can be a command-line module or class in a
script. Written to add this functionality to crds.diff.
"""
import sys

import difflib
from itertools import product
import numpy as np

# ==========================================================================

# Deferred
# from astropy.table import Table
# from astropy.io.fits import TableDataDiff
# from astropy.io.fits.hdu.hdulist import fitsopen
# from astropy.io.fits.hdu.table import _TableLikeHDU

# ==========================================================================

from crds.core  import cmdline

# ==========================================================================
# Utilities


def table_to_string(a_table):
    """Convert a table to a string list.

    Parameters
    ----------
    a_table : astropy.table.table.Table
        The table to convert to a string


    Returns
    -------
    result : sequence of strings
        A sequence of strings, where each string is one row with comma-separated
        column values

    """
    result = list()
    for element in a_table:
        result.append(str(list(element)).strip('[]'))
    return result


def list_intersection(a_list, b_list, transform=lambda element: element):
    """Return a list of the intersection of two lists.

    Parameters
    ----------
    a_list : sequence
        First list. The order of the returned list is determined by this list.

    b_list : sequence or set
        Second list.


    Returns
    -------
    result : list
        The intersection of the input lists with the transformation performed
        on each element

    Other Parameters
    ----------------
    transform : function(element)
        A function to perform on each element while the intersection is
        being executed.

"""

    # Convert the second list to a set, if necessary
    b_set = b_list
    if not isinstance(b_set, set):
        b_set = set(b_list)

    # Do the intersection and return a list.
    result = [transform(value) for value in a_list
              if transform(value) in b_set]

    return result


def get_hdulist(fits_reference):
    """ Open an HDU list from the fits reference.
    Note that the reference may already be an HDUList
    """
    # If the reference is a string, presume its a file path
    from astropy.io.fits.hdu.hdulist import fitsopen
    result = fits_reference
    if isinstance(fits_reference, str):
        try:
            result = fitsopen(fits_reference)
        except Exception as exc:
            raise IOError("error opening file (%s): %s: %s" %
                          (fits_reference, exc.__class__.__name__, exc.args[0])) from exc
    return result


def hdus_consistent(a_hdulist, b_hdulist):
    """Check that two HDUs are consistent

    Parameters
    ----------
        a_hdulist, b_hdulist: pyfits.HDUList

    Returns
    -------
    result : bool
        Return True

    Raises
    ------
    RuntimeError
        Will be raised if any of the following occur:
            - Different number of extensions
            - Corresponding extensions are of different types.

    """

    # Check that there are the same number of HDUs
    if len(a_hdulist) != len(b_hdulist):
        raise RuntimeError('HDUs have different lengths: FITS A = %d, FITS B = %d' % \
            (len(a_hdulist), len(b_hdulist)))

    # Loop through the HDUs and check types
    # If one is different, then abort.
    for index in range(len(a_hdulist)):
        if a_hdulist[index].header.get('XTENSION') != \
           b_hdulist[index].header.get('XTENSION'):
            raise RuntimeError('Extension %d different: FITS A = %s, FITS B = %s' % \
                                   (index,
                                    a_hdulist[index].header.get('XTENSION'),
                                    b_hdulist[index].header.get('XTENSION')))

    return True

def column_name_lower(table):
    """Rename all columns to lowercase

    Parameters
    ----------
    table : astropy.table.Table
        Table to rename all columns for.

    Returns
    -------
    Modifies table in place

    """
    for name in table.colnames:
        try:
            table.rename_column(name, name.lower())
        except:
            pass


def report_mode_diff(diff):
    """Generate text for mode differences.

    Parameters
    ----------
    diff : tuple of (a_table, b_table, opcodes)
        `a_table` and b_table are the astropy.table.Table
        objects that difflib.SequenceMatcher
        was executed on. `opcodes` is that difference.

    Returns
    -------
    result :
        A single string containing a human-readable version of the difference

    """

    # Check edge case where no changes exist.
    result = ''
    if diff:
        (a_table,
         b_table,
         opcodes) = diff

        if len(opcodes):

            # Initialize the masks
            mask_deleted = np.zeros(len(a_table), dtype=bool)
            mask_added = np.zeros(len(b_table), dtype=bool)
            mask_changed_a = np.zeros(len(a_table), dtype=bool)
            mask_changed_b = np.zeros(len(b_table), dtype=bool)

            for opcode in opcodes:

                # Get the opcode info.
                (operation,
                 from_start,
                 from_end,
                 to_start,
                 to_end) = opcode

                # If a deletion, return eport row removed.
                if operation == 'delete':
                    mask_deleted[from_start:from_end] = True

                # If an addition, report rows added.
                elif operation == 'insert':
                    mask_added[to_start:to_end] = True

                # If changes, report the changes
                elif operation == 'replace':
                    mask_changed_a[from_start:from_end] = True
                    mask_changed_b[to_start:to_end] = True

            # Create the report tables.
            deleted = a_table[mask_deleted]
            added = b_table[mask_added]
            changed_a = a_table[mask_changed_a]
            changed_b = b_table[mask_changed_b]

            # Now report
            if len(deleted):
                result += '\n        Missing Modes:\n'
                result += str(deleted) + '\n'
            if len(added):
                result += '\n        Duplicated Modes:\n'
                result += str(added) + '\n'
            if len(changed_a):
                result += '\n        Changed Modes:\n'
                result += '        From Table A:\n'
                result += str(changed_a)
                result += '\n\n        To Table B:\n'
                result += str(changed_b) + '\n'

    # That's all folks
    return result


def sm_filter_opcodes(sm_opcodes, code='equal'):
    """Filter SequenceMatcher opcodes

    Parameters
    ----------
    sm_opcodes : sequence
        The result of difflib.SequenceMatcher.get_opcodes()

    code : string
        The code to remove.

    Returns
    -------
    result : The sequence with the specified operation removed.

    """

    # Define the filter function
    condition = lambda opcode: opcode[0] != code

    # do the filtering
    return list(filter(condition, sm_opcodes))


@np.vectorize
def selected(element, wanted):
    """Determine whether an element is in a sequence or set

    This is a conveninece routine to be decorated by numpy to
    allow efficient use on numpy collections

    Parameters
    ----------
    element : object
        Object to look for

    wanted : sequence or set
        The collection to look in

    Returns
    -------
    result : bool
        True if element is in the collection
    """

    return element in wanted


# ==========================================================================
class RowDiff:
    """Perform FITS table difference by rows

    Modules that are based on FITSDiff, such as Diff, compare
    tabular data on a column-by-column basis. Rowdiff compares tabular data
    on a row-by-row basis, producing UNIX diff-like output instead.
    Non-tabular extensions are ignored.

    Parameters
    ----------
    fits_a, fits_b: string or HDUList objects
        The two FITS files to compare. If strings are given, they
        are presumed to be file paths to open.

    fields: sequence
        List of fields to compare on.

    ignore_fields: sequence
        List of fields to ignore. Cannot specify both fields and ignore_fields

    mode_fields: sequence
        List of fields that define modes to compare


    Returns
    -------
    self.diffs : tuple for each table extension
        This is either None for no differences, or a
        tuple consisting of:
            - If mode_fields is specified, the tuple is described by
              modediff
            - Otherwise the tuple is described by rowdiff

    See Also
    --------
    self.rowdiff : Function that does the row differencing
    self.modediff : Function that does the mode differencing

    Notes
    -----
    The FITS data to be compared are required to be similar: they must have
    the same number of extensions and the types of extensions must match.

    The parameters --fields and --ignore-fields define which columns
    are compared between each table extension. These are mutually
    exclusive parameters and an error will generate if both are specified.

    """

    def __init__(self,
                 a_fits,
                 b_fits,
                 fields=[],
                 ignore_fields=[],
                 mode_fields=[]):

        self.a_hdulist = a_fits
        self.b_hdulist = b_fits
        self.fields = [field.lower() for field in fields]
        self.ignore_fields = [field.lower() for field in ignore_fields]
        self.mode_fields = mode_fields
        self.summary_only = False
        self.consistent = False

        # Check that fields and ignore_fields are not both
        # specified.
        if self.fields and self.ignore_fields:
            raise RuntimeError('Both fields and ignore_fields' +
                               ' cannot be specified.')

        # Get the FITS HDU's.
        with get_hdulist(a_fits) as self.a_hdulist, \
             get_hdulist(b_fits) as self.b_hdulist:

            # Do basic consistency checking. The number of HDUs in each
            # HDUList must be the same and the type of HDU must match.
            try:
                self.consistent = hdus_consistent(self.a_hdulist, self.b_hdulist)
            except RuntimeError as exc:
                print("rowdiff:", str(exc))

            # Set the differencing function.
            if self.mode_fields:
                self.diff = self.modediff
            else:
                self.diff = self.rowdiff

            # Loop through the HDU's, pick out the tables, then diff them.
            # We only need to look at the first HDUlist because we have
            # already checked consistency.
            self.diffs = []
            if not self.consistent:
                return

            from astropy.io.fits.hdu.table import _TableLikeHDU
            for hdu_index in range(len(self.a_hdulist)):
                if isinstance(self.a_hdulist[hdu_index], _TableLikeHDU):
                    self.diffs.append((hdu_index,
                                       self.diff(self.a_hdulist[hdu_index].data,
                                                 self.b_hdulist[hdu_index].data)))

    def modediff(self, a_fitstable, b_fitstable):
        """Produce diff-like output for table contents comparison

        Parameters
        ----------
        self: RowDiff instance
        a_fitstable: HDUList object
            First FITS table to compare
        b_fitstable: HDUList object
            Second FITS table to compare

        Returns
        -------
        result : tuple of diffs for the following comparisons:
            - All modes and table A
            - All modes and table B
            - table A vs. table B
            - Difference in rows of the common modes
              of both table A and table B
            Each item is either None for no differences,
            or a tuple consisting of
                - SequenceMatcher object
                - difflib.unified_diff object

        """
        # Get the mode fields.
        # self.mode_fields can also specify values for those fields.
        # If that is the case, we need to first separate out the
        # fields from the list
        if isinstance(self.mode_fields, dict):
            mode_field_names = dict.keys(self.mode_fields)

            mode_constraints = {key: value for key, value in self.mode_fields.items() if value is not None}
        else:
            mode_field_names = self.mode_fields
            mode_constraints = {}

        # Do a full FITS Table Data diff
        from astropy.io.fits import TableDataDiff
        data_diff = TableDataDiff(a_fitstable, b_fitstable,
                                  ignore_fields=self.ignore_fields,
                                  numdiffs=1)

        # Ensure that the mode select columns exist in both tables.
        # If all columns don't exit, then abort.
        if not set(mode_field_names) <= data_diff.common_column_names:
            raise RuntimeError('Mode select columns are not in both tables.')

        # Get the set of fields that will be compared.
        if self.fields:
            fields_common = list_intersection(self.fields,
                                              data_diff.common_column_names)
        else:
            # This funny business is done because common_column_names
            # is a set and the order is undetermined. This forces the
            # order to be the same as the original table.
            fields_common = list_intersection(a_fitstable.columns.names,
                                              data_diff.common_column_names,
                                              lambda element: element.lower())

        # Convert from FITS table to Astropy Table
        from astropy.table import Table    # Deferred
        a_table = Table(a_fitstable)
        b_table = Table(b_fitstable)

        # Rename the columns to lowercase.
        column_name_lower(a_table)
        column_name_lower(b_table)

        # Sort on the mode fields. We do this on the full tables
        # because later on we are going to examin the full tables
        # for diffing.
        a_table.sort(mode_field_names)
        b_table.sort(mode_field_names)

        # Create tables with just the mode columns
        a_table_modes = a_table[mode_field_names]
        b_table_modes = b_table[mode_field_names]

        values_possible = list()
        for field in mode_field_names:
            values_possible.append(sorted(list(set(list(a_table_modes[field]) +
                                                   list(b_table_modes[field])))))
        values_combinations = list(product(*values_possible))

        # Create a table of the combinations
        vc_array = np.array(values_combinations,
                            dtype=a_table_modes.dtype)
        vc_table = Table(vc_array)

        # Setup to do the diffing. Convert everything to strings.
        a_string = table_to_string(a_table_modes)
        b_string = table_to_string(b_table_modes)
        modes_string = table_to_string(vc_table)

        # Diff between the all modes and first table.
        sm = difflib.SequenceMatcher()
        sm.set_seqs(modes_string, a_string)
        result_modes_vs_a = (vc_table,
                             a_table_modes,
                             sm.get_opcodes())

        # Diff between all modes and the second table.
        sm.set_seqs(modes_string, b_string)
        result_modes_vs_b = (vc_table,
                             b_table_modes,
                             sm.get_opcodes())

        # Diff between the two tables.
        sm.set_seqs(a_string, b_string)
        result_a_vs_b = (a_table_modes,
                         b_table_modes,
                         sm.get_opcodes())
        matching_blocks = sm.get_matching_blocks()

        # For the last bit of magic, compare the common modes
        # between the two tables by rowdiff.
        # First see if there was any data difference,
        common_mode_diffs = None
        if data_diff.diff_rows or \
           data_diff.diff_values:

            # Rebuild the tables with just the matching modes and the
            # desired columns.
            if len(matching_blocks) > 1:

                # Create tables for just the fields of interest.
                # Need to include the mode columns also.
                # This is done against the original table to ensure
                # that the column order is the same.
                fields_all = list_intersection(a_table.colnames,
                                               mode_field_names +
                                               fields_common)

                a_table_common_fields = a_table[fields_all]
                b_table_common_fields = b_table[fields_all]

                # Create the tables that will be built into.
                dtypes = []
                for index in range(len(a_table_common_fields.dtype)):
                    dtypes.append(a_table_common_fields.dtype[index])
                a_table_values = Table(names=a_table_common_fields.colnames,
                                       dtype=dtypes)
                b_table_values = Table(names=a_table_common_fields.colnames,
                                       dtype=dtypes)

                for block in matching_blocks:
                    (a_row, b_row, n_rows) = block
                    for row in range(n_rows):
                        a_table_values.add_row(a_table_common_fields[a_row + row])
                        b_table_values.add_row(b_table_common_fields[b_row + row])

                # If values for the modes were defined, then select
                # only those rows.
                if isinstance(self.mode_fields, dict):
                    selected_rows = np.array([True for index in
                                              range(len(a_table_values))])
                    for (field, values) in dict.items(self.mode_fields):
                        if values:
                            selected_rows = np.logical_and(selected_rows,
                                                           selected(a_table_values[field], values))

                    a_table_values = a_table_values[selected_rows]
                    b_table_values = b_table_values[selected_rows]

                # We will be using string-based difflib for further
                # operations, so convert the tables to strings.
                a_string = table_to_string(a_table_values)
                b_string = table_to_string(b_table_values)

                # Find the differences. First use SequenceMatcher to get a
                # very concise list of changes.
                sm = difflib.SequenceMatcher()
                sm.set_seqs(a_string, b_string)
                common_mode_diffs = (a_table_values,
                                     b_table_values,
                                     sm.get_opcodes())

        # That's all folks.
        return (result_modes_vs_a,
                result_modes_vs_b,
                result_a_vs_b,
                common_mode_diffs)

    def rowdiff(self, a_fitstable, b_fitstable):
        """Produce diff-like output for table contents comparison

        Parameters
        ----------
        self: RowDiff instance
        a_fitstable: HDUList object
            First FITS table to compare
        b_fitstable: HDUList object
            Second FITS table to compare

        Returns
        -------
        result : Either None or a tuple of
            - SequenceMatcher object
            - String containing the unified diff version of the diff.

        """

        # Do a full FITS Table Data diff
        from astropy.io.fits import TableDataDiff
        data_diff = TableDataDiff(a_fitstable, b_fitstable,
                                  ignore_fields=self.ignore_fields,
                                  numdiffs=1)

        # Shortcut. If data differences, then end.
        if not data_diff.diff_rows and \
           not data_diff.diff_values:
            return None

        # Get the set of fields that will be compared.
        if self.fields:
            fields_common = list_intersection(self.fields,
                                              data_diff.common_column_names)
        else:
            # This funny business is done because common_column_names
            # is a set and the order is undetermined. This forces the
            # order to be the same as the original table.
            fields_common = list_intersection(a_fitstable.columns.names,
                                              data_diff.common_column_names,
                                              lambda element: element.lower())

        # If there are no common fields, exit
        if not fields_common:
            return None

        # Convert from FITS table to Astropy Table
        from astropy.table import Table
        a_table = Table(a_fitstable)
        b_table = Table(b_fitstable)

        # Rename the columns to lowercase.
        column_name_lower(a_table)
        column_name_lower(b_table)

        # Limit to the fields desired.
        a_table = a_table[fields_common]
        b_table = b_table[fields_common]

        # We will be using string-based difflib for further
        # operations, so convert the tables to strings.
        a_string = table_to_string(a_table)
        b_string = table_to_string(b_table)

        # Find the differences. First use SequenceMatcher to get a
        # very concise list of changes.
        sm = difflib.SequenceMatcher()
        sm.set_seqs(a_string, b_string)
        sm_opcodes = sm.get_opcodes()

        # If there are changes, produce a text diff of the changes.
        result = None
        if sm.ratio() < 0.99:
            unified_diff = difflib.unified_diff(a_string, b_string,
                                                "Table A", "Table B")
            result = (sm_opcodes, unified_diff)

        # Return the opcodes
        return result

    def __str__(self):
        """Provide readable output

        Returns
        -------
        result : String
            String of human readable version of the RowDiff object.

        """

        # Initialize the result string.
        result = ''

        # Save time, see if there are any diffs.
        if len(self.diffs) > 0:

            # Mode difference reporting
            if self.mode_fields:
                diff_current = 0
                for (diff_current, diff) in self.diffs:
                    result += 'Difference for HDU extension #%d\n' % diff_current

                    (result_modes_vs_a,
                     result_modes_vs_b,
                     result_a_vs_b,
                     common_mode_diffs) = diff

                    result_mode = report_mode_diff(result_modes_vs_a)
                    if result_mode:
                        result += '\n    Table A changes:\n'
                        result += result_mode
                    else:
                        result += '\n    Table A has all modes.\n'

                    result_mode = report_mode_diff(result_modes_vs_b)
                    if result_mode:
                        result += '\n    Table B changes:\n'
                        result += result_mode
                    else:
                        result += '\n    Table B has all modes.\n'

                    result_mode = report_mode_diff(result_a_vs_b)
                    if result_mode:
                        result += '\n    Table A to B changes:\n'
                        result += result_mode
                    else:
                        result += '\n    Table A and B share all modes.\n'

                    result_mode = report_mode_diff(common_mode_diffs)
                    if result_mode:
                        result += '\n    Common mode changes:\n'
                        result += '    If there were duplicate modes, the following may be nonsensical.\n'
                        result += result_mode
                    else:
                        result += '\n    All common modes are equivalent.\n'

            # Row difference reporting
            else:
                result_temp = ''
                for (diff_current, diff) in self.diffs:
                    if diff:
                        (sm_opcodes, unified_diff) = diff
                        filtered_diff = sm_filter_opcodes(sm_opcodes)
                        if filtered_diff:
                            result_temp += 'Row differences for HDU extension #%d\n\n' % diff_current
                            result_temp += '    Summary:\n'
                            for opcode in filtered_diff:

                                op, a_start, a_end, b_start, b_end = opcode
                                a_end -= 1
                                b_end -= 1

                                if op == 'replace':
                                    result_temp += '        a rows %d-%d differ from b rows %d-%d\n' % \
                                                   (a_start, a_end, b_start, b_end)
                                elif op == 'delete':
                                    result_temp += '        Remove from a rows %d-%d\n' % (a_start, a_end)
                                elif op == 'insert':
                                    result_temp += '        Add to b rows %d-%d\n' % (b_start, b_end)
                                else:
                                    pass

                            if not self.summary_only:
                                result_temp += '\n    Row difference, unified diff format:\n'
                                for unified_diff_row in unified_diff:
                                    result_temp += '        %s\n' % unified_diff_row

                if result_temp:
                    result += result_temp
                else:
                    result = '    HDU extension #%d contains no differences' % diff_current

        # Return the string
        return result

# =========================================================================
class RowDiffScript(cmdline.Script):
    """Command line script to perform FITS table difference by rows

    Parameters
    ----------
    fits_a, fits_b: Paths or HDUList objects of the
                    two FITS files to compare.
    fields: List of fields to compare on.
    ignore_fields: List of fields to ignore.
    mode_fields: List of fields that define modes to compare

    Note: The parameters 'fields' and 'ignore_fields' are mutually exclusive.
          An error will be raised if both are specified.

    Returns
    -------
      object variables:
          diffs: tuple of the differences for each table extension found.
                 This is either None for no differences, or is again a
                 tuple consisting of:
                     - If mode_fields is specified, the tuple is described by
                       modediff
                     - Otherwise the tuple is described by rowdiff
      stdout: Human readable report.

    """

    description = """Command line script to perform FITS table difference by rows"""

    epilog = """
    Modules that are based on FITSDiff, such as Diff, compare
    tabular data on a column-by-column basis. Rowdiff compares tabular data
    on a row-by-row basis, producing UNIX diff-like output instead.
    Non-tabular extensions are ignored.

    The FITS data to be compared are required to be similar: they must have
    the same number of extensions and the types of extensions must match.

    The parameters --fields and --ignore-fields define which columns
    are compared between each table extension. These are mutually
    exclusive parameters and an error will generate if both are specified.

    An example:

    % crds rowdiff s9m1329lu_off.fits s9518396u_off.fits
    Row differences for HDU extension #1

        Summary:
            Remove from a rows 0-3
            Add to b rows 4-35

        Row difference, unified diff format:
            --- Table A

            +++ Table B

            @@ -1,8 +1,36 @@

            -1, '1993-12-01', 224.84801, 2.5362999, -30.488701
            -2, '1993-12-01', 314.35199, -52.258701, -5.0489001
            -3, '1993-12-01', 44.669998, 0.87, 47.959999
            -4, '1993-12-01', 135.22099, 55.4618, -6.1592002
             1, '1994-01-25', 224.84801, 2.5362999, -30.488701

    First a summary of the changes between the table extension is given.
    Then, row-by-row difference is given, using unified diff syntax.

    The parameter --mode-fields initiates a different algorithm.
    Here, it is presumed the tabular data contains columns that can essentially
    be treated as keys upon with rows are selected. The fields specified are those
    key columns.

    All possible coombinations of values are determined be examining both
    extensions. Then, each table is compared against both this list and between
    each other, looking for multiply specified combinations, missing combinations,
    and, for the common combinations between the tables, whether the rest of the
    rows are equivalent or not.

    An example:
        % python -m rowdiff s9m1329lu_off.fits s9518396u_off.fits --mode-fields=detchip,obsdate
        Difference for HDU extension #1

            Table A changes:

                Missing Modes:
        detchip  obsdate
        ------- ----------
              1 1994-06-16
              1 1995-09-23
            <lines removed>

            Table B changes:

                Missing Modes:
        detchip  obsdate
        ------- ----------
              1 1993-12-01
              2 1993-12-01
            <lines removed>

            Table A to B changes:

                Missing Modes:
        detchip  obsdate
        ------- ----------
              1 1993-12-01

                Duplicated Modes:
        detchip  obsdate
        ------- ----------
              4 1994-06-16
              4 1995-09-23
            <lines removed>

                Changed Modes:
                From Table A:
        detchip  obsdate
        ------- ----------
              2 1993-12-01
              3 1993-12-01
              4 1993-12-01

                To Table B:
        detchip  obsdate
        ------- ----------
              1 1994-06-16
              1 1995-09-23
              1 1997-11-02
            <lines removed>

            All common modes are equivalent.

    """

    # Define the user interface
    def add_args(self):
        """Define the command line interface"""

        self.add_argument("tableA", help="First table to compare")
        self.add_argument("tableB", help="Second table to compare")
        self.add_argument("--ignore-fields", help="List of fields to ignore",
                          type=str)
        self.add_argument("--fields",
                          help="List of fields to compare",
                          type=str)
        self.add_argument("--mode-fields",
                          help="List of fields to do a mode compare",
                          type=str)

    locate_file = cmdline.Script.locate_file_outside_cache

    # Main program
    def main(self):
        """Perform the differencing"""

        # Get the path to the fits files.
        tableA_path = self.locate_file(self.args.tableA)
        tableB_path = self.locate_file(self.args.tableB)

        # Expand out the input field lists.
        fields = []
        ignore_fields = []
        mode_fields = []
        if self.args.fields is not None:
            fields = self.args.fields.split(',')
        if self.args.ignore_fields is not None:
            ignore_fields = self.args.ignore_fields.split(',')
        if self.args.mode_fields is not None:
            mode_fields = self.args.mode_fields.split(',')

        print(RowDiff(tableA_path, tableB_path,
                      fields=fields,
                      ignore_fields=ignore_fields,
                      mode_fields=mode_fields))

if __name__ == "__main__":
    sys.exit(RowDiffScript()())

"""This module adds additional submission metadata and a programmatic interface
to the original commamnd line submission program as part of the file submission
streamlining project.
"""

import os
import sys
import yaml
from crds.core import log, config
from .submit import ReferenceSubmissionScript
import urllib
from functools import wraps
from textwrap import wrap
from tempfile import mkstemp

BASE_URLS = {
    'dev': {
        'hst':  'https://hst-crds-dev.stsci.edu/',
        'jwst': 'https://jwst-crds-dev.stsci.edu/', },
    'test': {
        'hst':  'https://hst-crds-test.stsci.edu/',
        'jwst': 'https://jwst-crds-test.stsci.edu/', },
    #'production': {
    #    'hst':  'https://hst-crds.stsci.edu/',
    #    'jwst': 'https://jwst-crds.stsci.edu/', },
    }

URL_DESCRIPTION = 'submission_form/redcat_description.yml'

NULL_FIELDTYPES = {
    'BooleanField'     : bool,
    'CharField'        : str,
    'TypedChoiceField' : str, }

# Preserve order of YAML dicts (from https://stackoverflow.com/a/52621703):
yaml.add_representer(dict, lambda self, data: yaml.representer.SafeRepresenter.represent_dict(self, data.items()))

class RedCatApiScript(ReferenceSubmissionScript):
    """This script extends the original CRDS command line submission
    system with extra meta-data previously captured by the submit_to_redcat
    script.
    """
    def __init__(self, *args, **kargs):
        self._extra_redcat_parameters = {}
        super(RedCatApiScript, self).__init__(*args, **kargs)

    def get_submission_args(self):
        """Returns the combined form parameter dictionary as a CRDS Struct defining
        the mapping from all form variables to their string values.
        """
        parameters = super(RedCatApiScript, self).get_submission_args()
        extra_parameters = self.get_extra_parameters()
        parameters.update(extra_parameters)
        return parameters

    def get_extra_parameters(self):
        """Return the form dictionary mapping form variables to value strings for
        new variables being added by the streamlining project.
        """
        # ... get and populate required form dictionary,  careful about
        # conflicts with baseclass.   See baseclass self.connection for
        # doing any web i/o.
        return self._extra_redcat_parameters
        
    def batch_submit_references(self):
        """Do a web re-post to the batch submit references web page."""
        return self._submission("/submission_form/redcat_submit/")

class RedCatSubmissionScript(RedCatApiScript):
    """This script extends the original CRDS command line submission
    system with extra meta-data previously captured by the submit_to_redcat
    script.
    """
    def add_args(self):
        super(RedCatSubmissionScript, self).add_args()
        self.add_argument("--redcat-parameters", type=str,
                     help="Path to YAML file defining extra ReDCaT parameters.")
    
    def get_extra_parameters(self):
        """Return the form dictionary mapping form variables to value strings for
        new variables being added by the streamlining project.
        """
        with open(self.args.redcat_parameters) as f:
            text = f.read()
            log.verbose("Raw YAML read:\n", text, verbosity=75)
            loaded = yaml.safe_load(text)
            log.verbose("ReDCaT parameters:\n", log.PP(loaded))
            return loaded



#def submit(submission_params, autoconfirm=True, wait=False):
#    """Submit reference files and meta information to CRDS
#
#    Parameters
#    ----------
#    submission_params: dict
#        The meta and reference file parameters that define the submission
#
#    autoconfirm: bool
#        Complete submission all the way into CRDS.
#
#    wait: bool 
#        Wait for the submission to complete before returning.
#        On  completion,  successful  submission  will be ready
#        for confirmation on web site unless autoconfirm is True.
#
#    Returns
#    -------
#    monitor: monitor object
#        The handle to use to monitor the status of the submission
#
#    """
#
#    # Login to CRDS
#
#    # Certify the reference files
#    # In the future this will include checking for duplicate submissions
#
#    # Convert the dict the the appropriate structure.
#    # This would involve the use of `add_argument`
#
#    # Post the reference files to the website
#
#    # Post the meta information to the website
#
#    # Return the monitor handle
#
#    script = RedcatApiScript("crds.submit --files {} "
#                             "--monitor-processing "
#                             "--wait-for-completion "
#                             "--wipe-existing-files "
#                             "--certify-files "
#                             "--log-time "
#                             "--stats --creator '{} Team' "
#                             "--description '{}'").format(
#            submit_files, instrument, description)
#    # script._extra_redcat_parameters = {}
#    script()


class Submission(object):
    ''' Client-side Redcat submission class.  Can be used to prepare, validate, and submit 
    CRDS submissions.
    
    Call `submission_obj.help()` to print details about the submission object form fields.
    
    Parameters:
        observatory (str, {hst, jwst}):  Used in determining which CRDS for submission
        string (str, {production, test, dev}):  Used in determining which CRDS for submission
    '''
    def __init__(self, observatory, string='dev', *args, **kwargs):
        observatory, string = observatory.lower(), string.lower()
        if observatory not in ['hst', 'jwst']:
            raise ValueError('Observatory "{}" must be either "hst" or "jwst".')
        if string not in ['dev', 'test', 'production']:
            raise ValueError('String "{}" must be either "production", "test", or "dev".')
        self._observatory = observatory
        self._string = string
        
        config.base_url = BASE_URLS[self.string][self.observatory]
        url = urllib.parse.urljoin(config.base_url, URL_DESCRIPTION)
        try:
            with urllib.request.urlopen(url) as req:
                self._form_description = yaml.safe_load(req)
        except (urllib.error.HTTPError, urllib.error.URLError, ) as e:
            print ('Check your network connection!')
            raise e
        # Convert list describing form to a dictionary (preserves order):
        self._form_description = {field['key']: field for field in self._form_description}
        for key in self._form_description:  self._form_description[key].pop('key')
        
        # Hard-code in change_level and description for now:
        self._form_description['change_level'] = {
            'type': 'TypedChoiceField',
            'choices': {'TRIVIAL', 'MODERATE', 'SEVERE'},
            'initial': 'SEVERE',
            'required': True,
            'label': 'Degree that new files are expected to impact science results.', }
        self._form_description['description'] = {
            'type': 'CharField',
            'required': True,
            'label': 'Information about file changes and expected impacts, include '
                     'instrument and type.  Formatting note: only alphanumeric, '
                     'periods, commas, dashes, and underscores are allowed', }
        
        self._all_keys = set(self._form_description.keys())
        self._required_keys = {x for x in self._form_description if self._form_description[x]['required']}
        self._optional_keys = {x for x in self._form_description if not self._form_description[x]['required']}
        
        self._fields = dict()  # Users should not modify this directly!
        for key in self._form_description:
            # Avoid field validation for initialization by accessing hidden dictionary directly:
            self._fields[key] = NULL_FIELDTYPES[self._form_description[key]['type']]()
            try:
                self[key] = self._form_description[key]['initial']
            except KeyError:
                pass
        
        self._files = set()  # Users should not modify this directly!
    
    def __repr__(self):
        return '<Submission Object {}-{}>:\nFields:  {}\nFiles:  {}'.format(
            self.observatory, self.string, 
            self._fields.__repr__(), 
            list(self.files))
    
    # ------------------------------------------------------------------------------------
    # Dictionary methods to handle form field manipulation:

    def __setitem__(self, key, value):
        ''' Intercept and enforce validation requirements on individual fields.
        Booleans values map to 'Yes' and 'No' str.
        '''
        if key not in self._all_keys:
            raise ValueError("Key not in submission form template:  '{}'".format(key))
        if (key in self._required_keys) and (value == ''):  # allow Boolean False
            raise ValueError("Field '{}' cannot be empty.".format(key))
        field_type = NULL_FIELDTYPES[self._form_description[key]['type']]
        
        # Interpret boolean values in choice fields as 'Yes' and 'No':
        if isinstance(value, bool) and ('choices' in self._form_description[key]) and \
            not (self._form_description[key]['type'] == 'BooleanField'):
            if value:
                value = 'Yes'
            else:
                value = 'No'
        if not isinstance(value, field_type):
            raise ValueError("'{}' must be of type {}".format(key, field_type.__name__))
        
        # Check if choice fields have allowed values:
        if ('choices' in self._form_description[key]) and \
           (self._form_description[key]['type'] != 'BooleanField'):
            matches = [x for x in self._form_description[key]['choices'] if x.lower() == value.lower()]
            if len(matches) != 1:
                raise ValueError("'{}' must be a valid choice: {{{}}}".format(key, 
                                 ', '.join(self._form_description[key]['choices'])))
            # Inherit case from matching choice:
            value = matches[0]
        
        self._fields[key] = value

    def __delitem__(self, key, *args, **kargs):
        ''' Reset self[key] to its default initialized value.
        '''
        if key in self:
            self._fields[key] = NULL_FIELDTYPES[self._form_description[key]['type']]()
            try:
                self[key] = self._form_description[key]['initial']
            except KeyError:
                pass
        else:
            raise KeyError(key)

    @wraps(dict.__getitem__)
    def __getitem__(self, key, *args, **kargs):
        return self._fields.__getitem__(key, *args, **kargs)
    
    @wraps(dict.__contains__)
    def __contains__(self, *args, **kargs):
        return self._fields.__contains__(*args, **kargs)
    
    @wraps(dict.get)
    def get(self, *args, **kargs):
        return self._fields.get(*args, **kargs)
    
    @wraps(dict.keys)
    def keys(self, *args, **kargs):
        return self._fields.keys(*args, **kargs)
    
    @wraps(dict.values)
    def values(self, *args, **kargs):
        return self._fields.values(*args, **kargs)
    
    @wraps(dict.items)
    def items(self, *args, **kargs):
        return self._fields.items(*args, **kargs)
    
    # ------------------------------------------------------------------------------------
    # Set methods to handle filename manipulation:
    
    def add_file(self, filename):
        ''' Add a file to the submission.  Calls crds.certify() on the file.'''
        if not os.access(filename, os.R_OK):
            raise FileNotFoundError("'{}' does not exist or is not readable.".format(filename))

        self._files.add(filename)

    @wraps(set.remove)
    def remove_file(self, filename, *args, **kargs):
        self._files.remove(filename, *args, **kargs)

    # ------------------------------------------------------------------------------------
    # Class properties protected from direct user manipulation:

    @property
    def observatory(self):
        ''' Instantiated for HST or JWST.'''
        return self._observatory

    @property
    def string(self):
        ''' Instantiated for production, test, or dev string.'''
        return self._string

    @property
    def files(self):
        ''' Set of files associated with the submission.'''
        return frozenset(self._files)
    
    # ------------------------------------------------------------------------------------
    # Custom methods:
    
    def help(self):
        ''' Print help text derived from CRDS instance specified.'''
        # Can't easily overwrite __doc__ dynamically.
        for key, field in self._form_description.items():
            print (key, ' (', NULL_FIELDTYPES[self._form_description[key]['type']].__name__, 
                ', optional)' if not field.get('required', False) else ')', '\n', '-'*len(key), sep='')
            print ('\n'.join(wrap(field['label'])))
            if 'help_text' in field:
                print ('\n'.join(wrap(field['help_text'])))
            if 'choices' in field:
                print ('Valid choices:')
                print ('  {', ', '.join(["'{}'".format(x) for x in field['choices']]), '}', sep='')
            print ()
    
    def validate(self):
        ''' Validate the object for submission to CRDS.'''
        if (set(self.keys()) - self._optional_keys) != self._required_keys:
            raise Exception('Extra/missing keys')
        
        # Check for all empty required keys at once to raise one exception:
        empty_keys = {key for key in self._required_keys if self[key] == ''}  # Don't flag False booleans
        if empty_keys:
            raise ValueError('These keywords cannot be empty:\n    ' + '\n    '.join(empty_keys))

        # Make sure files were associated with the submission:
        if len(self.files) == 0:
            raise Exception('No files have been added to submission.  '
                            'Use the `submission_obj.add_file()` method.')
        
        # More validation...
    
    @wraps(yaml.dump)
    def yaml(self, *args, **kargs):
        ''' YAML representation of this submission object.'''
        return yaml.dump(dict(self), *args, **kargs)
    
    def submit(self):
        ''' Validate submission form, upload to CRDS staging, handle server-side 
        submission errors, drop client-side lock on success.
        '''
        # Upload the form
        # Handle returned server-side errors
        # On success, server-side lock is dropped.  Change client-side lock_status.
        
        self.validate()
        
        extra_fields = self._fields.copy()
        #extra_fields.pop('description')
        extra_fields.pop('change_level')
        
        yml_handle, yml_name = mkstemp(suffix='.yml')
        with open(yml_name, 'w') as f:
            yaml.dump(extra_fields, stream=f)
        print ('YAML FILE:  ', yml_name)
        try:
            # "--verbosity 80 "
            call_to_RedCatApiScript = ("crds.submit --files {} "
                                       "--monitor-processing "
                                       "--wait-for-completion "
                                       "--wipe-existing-files "
                                       "--certify-files "
                                       "--log-time "
                                       "--stats --creator {} "
                                       "--change-level {} "
                                       "--description {} ").format(
                ' '.join(self.files),  #["'{}'".format(x) for x in self.files]), 
                self['instrument'], 
                self['change_level'], 
                self['description'])
            print (call_to_RedCatApiScript)
            #crds.submit --files xa81715gj_ccd.fits --monitor-processing --wait-for-completion 
            #--wipe-existing-files --certify-files --log-time --stats 
            #--creator 'stis Team' --change-level MODERATE 
            #--description 'Updating STIS CCDTAB with new readnoise values starting 2017-Jan-03.' 
                        
            # usage: crds.submit [-h] [--files [FILES [FILES ...]]]
            #        [--derive-from-context DERIVE_FROM_CONTEXT]
            #        [--change-level {SEVERE,MODERATE,TRIVIAL}]
            #        [--creator CREATOR] [--description DESCRIPTION]
            #        [--dont-auto-rename] [--dont-compare-old-reference]
            #        [--username USERNAME] [--monitor-processing]
            #        [--wait-for-completion]
            #        [--submission-kind {batch,certify,none}]
            #        [--wipe-existing-files] [--keep-existing-files]
            #        [--certify-files] [--logout]
            #        [--redcat-parameters REDCAT_PARAMETERS] [-v]
            #        [--verbosity VERBOSITY] [--dump-cmdline] [-R] [-I] [-V]
            #        [-J] [-H] [--stats] [--profile PROFILE] [--log-time]
            #        [--pdb] [--debug-traps]
            #
            # crds.submit: error: unrecognized arguments: Team' STIS CCDTAB with new readnoise values starting 2017-Jan-03.'
            # An exception has occurred, use %tb to see the full traceback.

            
            script = RedCatApiScript( call_to_RedCatApiScript )
            
            script._extra_redcat_parameters = extra_fields  # Use update instead?
            
            #script = RedCatApiScript("crds.submit --files {} "
            #                         "--monitor-processing "
            #                         "--wait-for-completion "
            #                         "--wipe-existing-files "
            #                         "--certify-files "
            #                         "--log-time "
            #                         "--stats --creator '{} Team' "
            #                         "--redcat-parameters '{}' "
            #                         "--change-level {} "
            #                         "--description '{}'".format(
            #                ' '.join(self.files), 
            #                self['instrument'], 
            #                yml_name, 
            #                self['change_level'], 
            #                self['description']))
            
            
            script()
        finally:
            os.remove(yml_name)

def main():
    """Run the command line program version of the extended batch submit which
    loads extended parameters from a YAML input file.
    """
    script = RedCatSubmissionScript()
    return script()

if __name__ == "__main__":
    sys.exit(main())

import os
import shutil
import tempfile
from nose.tools import assert_equals, assert_not_equals, assert_is, assert_true, raises
from crds.submit import Submission, NoFilesSelected
from crds.tests import test_config
import mock

# To run:
#   nosetests -v unit_tests.py

TEMPFILES = ['ipppssoot_ccd.fits', 'opppssoot_bia.fits']

# Mocked urllib.request to .../redcat_description.yml:
FORM_DESCRIPTION_YML = '''\
- {help_text: 'Who are you?', key: deliverer, label: Name of deliverer, required: true,
  type: CharField}
- {help_text: Comma-delimited list (optional), key: other_email, label: Other e-mail
    adresses to send notifications, required: false, type: CharField}
- choices: [acs, cos, nicmos, stis, synphot, wfc3, wfpc2]
  initial: acs
  key: instrument
  label: Instrument  (All submitted files should match this instrument.  This instrument
    will be locked for your submission exclusively)
  required: true
  type: TypedChoiceField
- {key: file_type, label: 'Type of files (Bias, Dark, etc.)', required: true, type: CharField}
- choices: [false, true]
  initial: false
  key: history_updated
  label: Has HISTORY section in the primary header been updated to describe in detail
    the reason for delivery and how the files were created?
  required: false
  type: BooleanField
- choices: [false, true]
  initial: false
  key: pedigree_updated
  label: Has PEDIGREE keyword been checked and updated as necessary?
  required: false
  type: BooleanField
- choices: [false, true]
  initial: false
  key: keywords_checked
  label: Has COMMENT been checked?
  required: false
  type: BooleanField
- choices: [false, true]
  initial: false
  key: descrip_updated
  label: Was the DESCRIP keyword updated with a summary of why the files were updated
    or created?
  required: false
  type: BooleanField
- choices: [false, true]
  initial: false
  key: useafter_updated
  label: Has the USEAFTER keyword been checked, and if necessary, updated?
  required: false
  type: BooleanField
- choices: [N/A, 'No', 'Yes']
  help_text: N/A for ETC Files Only
  initial: N/A
  key: useafter_matches
  label: If the reference files are replacing previous versions, do the new USEAFTER
    dates exactly match the old ones?
  required: true
  type: TypedChoiceField
- choices: [N/A, 'No', 'Yes']
  help_text: optional
  initial: N/A
  key: compliance_verified
  label: Verification for compliance complete (fits, certify, etc. or N/A)
  required: true
  type: TypedChoiceField
- choices: [false, true]
  initial: false
  key: ingest_files
  label: Should the affected files be reprocessed?
  required: false
  type: BooleanField
- choices: [false, true]
  initial: false
  key: etc_delivery
  label: Should the files be submitted to the ETC?
  required: false
  type: BooleanField
- choices: [false, true]
  initial: false
  key: jwst_etc
  label: Are these JWST ETC files?
  required: false
  type: BooleanField
- {key: calpipe_version, label: Files run through the current version of the calibration
    software being used by the pipeline or PYSYNPHOT and ETC (yes/no and version number),
  required: true, type: CharField}
- choices: [false, true]
  initial: false
  key: replacement_files
  label: Are any files replacing old reference files (deliveries can be a mix of files
    that are or are not replacing old files) (yes/no)
  required: false
  type: BooleanField
- {key: old_reference_files, label: 'If yes, list them here', required: false, type: CharField}
- choices: [N/A, 'No', 'Yes']
  initial: N/A
  key: replacing_badfiles
  label: If the files being replaced are bad, and should not be used with any data,
    please indicate this here
  required: true
  type: TypedChoiceField
- {help_text: Comma-delimited list (optional), key: jira_issue, label: Any JIRA issues
    filed in regard to the references being delivered (e.g. "REDCAT-25"), required: false,
  type: CharField}
- {key: table_rows_changed, label: 'If files are tables, please indicate exactly which
    rows have changed', required: false, type: CharField}
- {key: modes_affected, label: 'Please indicate which modes (e.g. all the STIS, FUVMAMA,
    E140L modes) are affected by the changes in the files', required: true, type: CharField}
- {key: correctness_testing, label: Description of how the files were tested for correctness,
  required: true, type: CharField}
- {key: additional_considerations, label: Additional considerations, required: false,
  type: CharField}
'''

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

class TestSubmission(object):
    @classmethod
    @mock.patch('crds.submit.rc_submit.urllib.request.urlopen', autospec=True)
    def setup_class(cls, urlopen):
        '''This method is run once for each class before any tests are run.'''
        cls.old_state = test_config.setup()

        # Create a temporary directory:
        cls.tmpdir = tempfile.mkdtemp(prefix='tmp_rc_submit_')

        # Create empty test files in the temporary directory:
        cls.tempfiles = [os.path.join(cls.tmpdir, x) for x in TEMPFILES]
        for filename in cls.tempfiles:
            touch(filename)

        # Create a file handle to use as a mockup of the urllib.request object:
        cls.mockup_form = os.path.join(cls.tmpdir, 'mocked_redcat_description.yml')
        with open(cls.mockup_form, 'w') as f:
            f.write(FORM_DESCRIPTION_YML)
        urlopen.return_value = open(cls.mockup_form)

        # Instantiate the Submission object used in these tests:
        cls.s = Submission('hst', 'dev', context='hst_0723.pmap')

    @classmethod
    def teardown_class(cls):
        '''This method is run once for each class after all tests are run.'''
        # Remove temporary directory and all files contained therein:
        shutil.rmtree(cls.tmpdir)
        test_config.cleanup(cls.old_state)

    @raises(KeyError)
    def test_badkey(self):
        self.s['bad_key'] = 'some value'

    def test_goodvalue_char(self):
        self.s['file_type'] = 'bias'

    def test_goodvalue_bool(self, key='history_updated'):
        self.s[key] = True
        assert_is(self.s[key], True)
        self.s[key] = False
        assert_is(self.s[key], False)

    def test_goodvalue_trinary(self, key='compliance_verified'):
        # Set with Booleans:
        self.s[key] = True
        assert_equals(self.s[key], 'Yes')
        self.s[key] = False
        assert_equals(self.s[key], 'No')

        # Set with strings:
        self.s[key] = 'Yes'
        assert_equals(self.s[key], 'Yes')
        self.s[key] = 'yes'  # Handle different case
        assert_equals(self.s[key], 'Yes')
        self.s[key] = 'No'
        assert_equals(self.s[key], 'No')
        self.s[key] = 'n/a'  # Handle different case
        assert_equals(self.s[key], 'N/A')

    @raises(ValueError)
    def test_badtype(self):
        self.s['calpipe_version'] = 123  # Expects a str

    @raises(ValueError)
    def test_badvalue_trinary(self, key='compliance_verified'):
        self.s[key] = 'bad value'

    @raises(ValueError)
    def test_badvalue_choices(self):
        self.s['change_level'] = 'bad choice'

    @raises(ValueError)
    def test_emptyvalue_char(self):
        self.s['file_type'] = ''

    @raises(ValueError)
    def test_emptyvalue_char(self, key='file_type'):
        self.s[key] = ''  # Required field

    def test_emptyvalue_optional(self):
        self.s['additional_considerations'] = ''  # Optional field

    def test_resetfield(self, key='deliverer'):
        new_value = 'Wombat'
        self.s[key] = new_value
        assert_equals(self.s[key], new_value)
        del self.s[key]
        assert_not_equals(self.s[key], new_value)  # Also assumes KeyError is not thrown!

    def test_addfiles(self):
        for filename in self.tempfiles:
            self.s.add_file(filename)

    @raises(FileNotFoundError)
    def test_addbadfile(self):
        self.s.add_file(os.path.join(self.tmpdir, 'missing_file.fits'))

    def test_rmfile(self):
        for filename in self.tempfiles:
            self.s.add_file(filename)
        self.s.remove_file(list(self.tempfiles)[0])
        assert_equals( len(self.s.files), len(self.tempfiles)-1 )

    @raises(KeyError)
    def test_rmbadfile(self):
        for filename in self.tempfiles:
            self.s.add_file(filename)
        self.s.remove_file('bad_filename.fits')

    def test_yaml(self):
        assert_true(self.s.yaml)

    def test_help(self):
        self.s.help()  # Prints stuff

    @raises(ValueError)
    def test_validate_emptykey(self, key='file_type'):
        del self.s[key]  # Resets to empty str
        self.s.validate()

    @raises(NoFilesSelected)
    def test_validate_emptyfiles(self):
        for filename in self.s.files:
            self.s.remove_file(filename)

        # Do something here to pass field validation checks:
        self.s['file_type']           = 'value'
        self.s['correctness_testing'] = 'value'
        self.s['deliverer']           = 'value'
        self.s['description']         = 'value'
        self.s['calpipe_version']     = 'value'
        self.s['modes_affected']      = 'value'
        self.s['instrument']          = 'stis'  # Only works for HST

        self.s.validate()

    def test_validate(self):
        self.s.add_file(list(self.tempfiles)[0])

        # Do something here to pass field validation checks:
        self.s['file_type']           = 'value'
        self.s['correctness_testing'] = 'value'
        self.s['deliverer']           = 'value'
        self.s['description']         = 'value'
        self.s['calpipe_version']     = 'value'
        self.s['modes_affected']      = 'value'
        self.s['instrument']          = 'stis'  # Only works for HST

        self.s.validate()

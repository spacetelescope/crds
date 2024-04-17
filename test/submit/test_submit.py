from pytest import mark, fixture
import os
from crds.submit import Submission, NoFilesSelected
import mock


def mock_urlopen():
    with mock.patch('crds.submit.rc_submit.urllib.request.urlopen', autospec=True) as urlopen:
        return urlopen

@mark.hst
@mark.submit
class TestSubmit(object):


    @fixture(autouse=True)
    def _set_config(self, hst_shared_cache_state, submit_test_files, tmp_rc, mock_submit_form):
        hst_shared_cache_state.url = 'https://hst-crds.stsci.edu'
        hst_shared_cache_state.config_setup()
        self._config = hst_shared_cache_state
        self.tempfiles = submit_test_files
        self.tmp_rc = tmp_rc
        # Mocked urllib.request to .../redcat_description.yml:
        urlopen = mock_urlopen()
        urlopen.return_value = mock_submit_form
        self.s = Submission('hst', 'ops', context='hst_0723.pmap')

    def ValErr(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except ValueError:
                assert True
                return
        return wrapper

    def KeyErr(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except KeyError:
                assert True
                return
        return wrapper

    def NfsErr(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except NoFilesSelected:
                assert True
                return
        return wrapper

    @KeyErr
    def test_badkey(self):
        self.s['bad_key'] = 'some value'

    def test_goodvalue_char(self):
        self.s['file_type'] = 'bias'

    def test_goodvalue_bool(self, key='history_updated'):
        self.s[key] = True
        assert self.s[key] is True
        self.s[key] = False
        assert self.s[key] is False

    def test_goodvalue_trinary(self, key='compliance_verified'):
        # Set with Booleans:
        self.s[key] = True
        assert self.s[key] == 'Yes'
        self.s[key] = False
        assert self.s[key] == 'No'

        # Set with strings:
        self.s[key] = 'Yes'
        assert self.s[key] == 'Yes'
        self.s[key] = 'yes'  # Handle different case
        assert self.s[key] == 'Yes'
        self.s[key] = 'No'
        assert self.s[key] == 'No'
        self.s[key] = 'n/a'  # Handle different case
        assert self.s[key] == 'N/A'

    @ValErr
    def test_badtype(self):
        self.s['calpipe_version'] = 123  # Expects a str

    @ValErr
    def test_badvalue_trinary(self, key='compliance_verified'):
        self.s[key] = 'bad value'

    @ValErr
    def test_badvalue_choices(self):
        self.s['change_level'] = 'bad choice'

    @ValErr
    def test_emptyvalue_char(self):
        self.s['file_type'] = ''

    @ValErr
    def test_emptyvalue_char(self, key='file_type'):
        self.s[key] = ''  # Required field

    def test_emptyvalue_optional(self):
        self.s['additional_considerations'] = ''  # Optional field

    def test_resetfield(self, key='deliverer'):
        new_value = 'Wombat'
        self.s[key] = new_value
        assert self.s[key] == new_value
        del self.s[key]
        assert self.s[key] != new_value  # Also assumes KeyError is not thrown!

    def test_addfiles(self):
        for filename in self.tempfiles:
            self.s.add_file(filename)

    def test_addbadfile(self):
        try:
            self.s.add_file(os.path.join(self.tmp_rc, 'missing_file.fits'))
        except FileNotFoundError:
            assert True

    def test_rmfile(self):
        for filename in self.tempfiles:
            self.s.add_file(filename)
        self.s.remove_file(list(self.tempfiles)[0])
        assert len(self.s.files) == len(self.tempfiles)-1

    @KeyErr
    def test_rmbadfile(self):
        for filename in self.tempfiles:
            self.s.add_file(filename)
        self.s.remove_file('bad_filename.fits')

    def test_yaml(self):
        assert self.s.yaml is not None

    def test_help(self):
        self.s.help()  # Prints stuff

    @ValErr
    def test_validate_emptykey(self, key='file_type'):
        del self.s[key]  # Resets to empty str
        self.s.validate()

    @NfsErr
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
        self.s['description']         = 'Dash-es under_scores, commas, periods. 1234567890 += fwd/slash.'
        self.s['calpipe_version']     = 'value'
        self.s['modes_affected']      = 'value'
        self.s['instrument']          = 'stis'  # Only works for HST
        self.s.validate()

    @ValErr
    def test_invalid_description(self):
        self.s.add_file(list(self.tempfiles)[0])
        some_invalid_chars = ['!', '@', '$', '%', '^', '*', '(', ')', '~', '`', '"', '?', '|', '{', '}', '[', ']', ':', ';', '<', '>']
        # Do something here to pass field validation checks:
        self.s['file_type']           = 'value'
        self.s['correctness_testing'] = 'value'
        self.s['deliverer']           = 'value'
        self.s['calpipe_version']     = 'value'
        self.s['modes_affected']      = 'value'
        self.s['instrument']          = 'stis'  # Only works for HST
        for bad in some_invalid_chars:
            self.s['description'] = f'This desc is invalid because it contains a {bad} char.'
            self.s.validate()
    
    @ValErr
    def test_multiple_invalid_chars(self):
        self.s.add_file(list(self.tempfiles)[0])
        self.s['file_type']           = 'value'
        self.s['correctness_testing'] = 'value'
        self.s['deliverer']           = 'value'
        self.s['calpipe_version']     = 'value'
        self.s['modes_affected']      = 'value'
        self.s['instrument']          = 'stis'  # Only works for HST
        invalid_strings = [
          "This %RFD is invalid",
          "This <RFD> is still invalid",
          "This {RFD is $invalid."
        ]
        for bad in invalid_strings:
            self.s['description'] = bad
            self.s.validate()

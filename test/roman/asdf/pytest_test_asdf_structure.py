import os
from pytest import (
    mark,
    raises
)

from crds.certify.certify import check_asdf_tag

@mark.asdf
@mark.roman
class ASDFValidationPyTests:

    def pytest_test_can_validate_top_level_tag(self):
        known_good_asdf_file_path = f"{os.environ['CRDS_TESTING_CACHE']}/good_tag_flat_file.asdf"
        assert check_asdf_tag(known_good_asdf_file_path) == True

    def pytest_test_tag_validation_raises_exception(self):
        known_bad_asdf_file_path = f"{os.environ['CRDS_TESTING_CACHE']}/bad_tag_flat_file.asdf"
        assert raises(check_asdf_tag(known_bad_asdf_file_path))

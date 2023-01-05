import os

import pytest

from crds.certify.certify import check_asdf_tag


@pytest.mark.asdf
@pytest.mark.roman
def test_can_validate_top_level_tag():
    known_good_asdf_file_path = f"{os.environ['CRDS_TESTING_CACHE']}/good_tag_flat_file.asdf"
    assert check_asdf_tag(known_good_asdf_file_path) == True


@pytest.mark.asdf
@pytest.mark.roman
def test_tag_validation_raises_exception():
    known_bad_asdf_file_path = f"{os.environ['CRDS_TESTING_CACHE']}/bad_tag_flat_file.asdf"
    assert pytest.raises(check_asdf_tag(known_bad_asdf_file_path))

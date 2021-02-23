import unittest
import pathlib

from crds.tests import test_config
from crds.core import heavy_client
from crds.core.exceptions import CrdsLookupError

from nose.tools import raises


class TestRoman(unittest.TestCase):
    """ TestRoman is a collection of crds unit tests for ROMAN.
    """
    def setUp(self):
        self.old_state = test_config.setup(
            url="https://roman-crds-serverless.stsci.edu",
            observatory="roman",
            cache=test_config.CRDS_TESTING_CACHE
        )

    def tearDown(self):
        test_config.cleanup(self.old_state)

    def test_getreferences_with_valid_header(self):
        """ test_getreferences_with_valid_header: test satisfies Roman 303.1
        """
        result = heavy_client.getreferences(
            {
                "META.INSTRUMENT.NAME": "WFI",
                "META.INSTRUMENT.DETECTOR": "WFI01",
                "META.EXPOSURE.TYPE": "WFI_IMAGE",
                "META.OBSERVATION.DATE": "2020-02-01",
                "META.OBSERVATION.TIME": "00:00:00",
            },
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=["dark"]
        )

        assert pathlib.Path(result["dark"]).name == "roman_wfi_dark_0001.asdf"

    @raises(CrdsLookupError)
    def test_getreferences_with_invalid_header(self):
        """ test_getreferences_with_invalid_header: test satisfies Roman 303.1
        """
        heavy_client.getreferences(
            {
                "META.INSTRUMENT.NAME": "WFI",
                "META.INSTRUMENT.DETECTOR": "WFI02",
                "META.EXPOSURE.TYPE": "WFI_IMAGE",
                "META.OBSERVATION.DATE": "2020-02-01",
                "META.OBSERVATION.TIME": "00:00:00",
            },
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=["dark"]
        )

import os
import subprocess
import unittest
import pathlib


from crds.core import heavy_client
from crds.core.exceptions import CrdsLookupError

from crds.tests import test_config
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

    def test_list_references(self):
        """ test_list_references: test satisfies Roman 303.2
        """
        env = os.environ.copy()

        expected_result = {
            "roman_wfi_flat_0003.asdf",
            "roman_wfi_dark_0001.asdf"
        }

        list_command = [
            'crds',
            'list',
            '--references',
            '--contexts',
            'roman_wfi_0004.imap'
        ]

        p = subprocess.Popen(
            list_command,
            env=env,
            stdout=subprocess.PIPE

        )
        results, err = p.communicate()
        results = results.decode('ascii').split("\n")

        assert {item for item in results if item} == expected_result

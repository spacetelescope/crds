import os
import subprocess
import unittest
import pathlib

from crds.core import heavy_client
from crds.client import api
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

    def test_getreferences_with_valid_header_ISOT_fmt(self):
        """ test_getreferences_with_valid_header: test satisfies Roman 303.1 and 628.1
        """
        result = heavy_client.getreferences(
            {
                "ROMAN.META.INSTRUMENT.NAME": "WFI",
                "ROMAN.META.INSTRUMENT.DETECTOR": "WFI01",
                "ROMAN.META.EXPOSURE.TYPE": "WFI_IMAGE",
                "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01T00:00:00"
            },
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=["dark"]
        )

        assert pathlib.Path(result["dark"]).name == "roman_wfi_dark_0001.asdf"
    
    def test_getreferences_with_valid_header_ISO_fmt(self):
        """ test_getreferences_with_valid_header: test satisfies Roman 303.1 and 628.1
        """
        result = heavy_client.getreferences(
            {
                "ROMAN.META.INSTRUMENT.NAME": "WFI",
                "ROMAN.META.INSTRUMENT.DETECTOR": "WFI01",
                "ROMAN.META.EXPOSURE.TYPE": "WFI_IMAGE",
                "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01 00:00:00"
            },
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=["dark"]
        )

        assert pathlib.Path(result["dark"]).name == "roman_wfi_dark_0001.asdf"

        result = heavy_client.getreferences(
            {
                "ROMAN.META.INSTRUMENT.NAME": "WFI",
                "ROMAN.META.INSTRUMENT.DETECTOR": "WFI01",
                "ROMAN.META.EXPOSURE.TYPE": "WFI_GRISM",
                "ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT": "GRISM",
                "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01T00:00:00"
            },
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=["flat"]
        )

        assert pathlib.Path(result["flat"]).name == "roman_wfi_flat_0004.asdf"

        result = heavy_client.getreferences(
            {
                "ROMAN.META.INSTRUMENT.NAME": "WFI",
                "ROMAN.META.INSTRUMENT.DETECTOR": "WFI01",
                "ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT": "F213",
                "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01T00:00:00"
            },
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=["distortion"]
        )

        assert pathlib.Path(result["distortion"]).name == "roman_wfi_distortion_0001.asdf"


    @raises(CrdsLookupError)
    def test_getreferences_with_invalid_header(self):
        """ test_getreferences_with_invalid_header: test satisfies Roman 303.1
        """
        heavy_client.getreferences(
            {
                "ROMAN.META.INSTRUMENT.NAME": "WFI",
                "ROMAN.META.INSTRUMENT.DETECTOR": "WFI02",
                "ROMAN.META.EXPOSURE.TYPE": "WFI_IMAGE",
                "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01T00:00:00"
            },
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=["dark"]
        )

    def test_list_references(self):
        """ test_list_references: test satisfies Roman 303.2 and 628.2
        """
        env = os.environ.copy()

        expected_result = {
            "roman_wfi_flat_0004.asdf",
            "roman_wfi_distortion_0001.asdf",
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

    def test_get_aui_bestrefs_wfi_imaging_level2(self):
        """ test_get_aui_bestrefs_wfi_imaging_level2: test satisfies Roman SOC 670

        The test retrieves headers from the archive for datasets with criteria matching 
        exposure_type=WFI_IMAGE and productLevel=2, then calls the archive API to produce 
        a list of best references for regenerating the dataset(s).
        """
        context = "roman_0039.pmap"
        dataset_ids = [
            'R0000101001001001001_01101_0001.WFI16:R0000101001001001001_01101_0001.WFI16',
        ]
        # get headers from archive
        headers = api.get_dataset_headers_by_id(context, dataset_ids)
        # confirm roman.meta.exposure.type = WFI_IMAGE, productLevel = 2
        for _, h in headers.items():
            assert h["ROMAN.META.EXPOSURE.TYPE"] == "WFI_IMAGE"
            assert h["productLevel"] == "2"
        # get best references
        refs = api.get_aui_best_references(context, dataset_ids)
        expected_result = {
            'R0000101001001001001_01101_0001.WFI16:R0000101001001001001_01101_0001.WFI16': [
                True,
                [
                'roman_wfi_dark_0231.asdf',
                'roman_wfi_distortion_0016.asdf',
                'roman_wfi_flat_0231.asdf',
                'roman_wfi_gain_0055.asdf',
                'roman_wfi_linearity_0087.asdf',
                'roman_wfi_mask_0066.asdf',
                'roman_wfi_photom_0054.asdf',
                'roman_wfi_readnoise_0207.asdf',
                'roman_wfi_saturation_0076.asdf'
                ]
            ]
        }
        assert refs == expected_result

    def test_get_aui_bestrefs_wfi_spectroscopy_level2(self):
        """test_get_aui_bestrefs_wfi_spectroscopy_level2: test satisfies Roman SOC 673

        The test retrieves headers from the archive for datasets with criteria matching 
        exposure_type=WFI_PRISM or WFI_GRISM and productLevel=2, then calls the archive API 
        to produce a list of best references for regenerating the dataset(s).
        """
        context = "roman_0039.pmap"
        dataset_ids = [
            'R0000201001001001002_01101_0001.WFI01:R0000201001001001002_01101_0001.WFI01',
            'R0000201001001001003_01101_0001.WFI01:R0000201001001001003_01101_0001.WFI01'
        ]
        # get headers from archive
        headers = api.get_dataset_headers_by_id(context, dataset_ids)
        # confirm roman.meta.exposure.type = WFI_PRISM or WFI_GRISM, productLevel = 2
        for _, h in headers.items():
            assert h["ROMAN.META.EXPOSURE.TYPE"] in ["WFI_PRISM", "WFI_GRISM"]
            assert h["productLevel"] == "2"
        # get bestrefs for datasets
        refs = api.get_aui_best_references(context, dataset_ids)
        expected_result = {
            'R0000201001001001002_01101_0001.WFI01:R0000201001001001002_01101_0001.WFI01': [
                True,
                [
                    'roman_wfi_dark_0218.asdf',
                    'roman_wfi_distortion_0008.asdf',
                    'roman_wfi_gain_0086.asdf',
                    'roman_wfi_linearity_0078.asdf',
                    'roman_wfi_mask_0078.asdf',
                    'roman_wfi_photom_0056.asdf',
                    'roman_wfi_readnoise_0174.asdf',
                    'roman_wfi_saturation_0106.asdf'
                    ]
            ],
            'R0000201001001001003_01101_0001.WFI01:R0000201001001001003_01101_0001.WFI01': [
                True,
                [
                    'roman_wfi_dark_0218.asdf',
                    'roman_wfi_distortion_0008.asdf',
                    'roman_wfi_gain_0086.asdf',
                    'roman_wfi_linearity_0078.asdf',
                    'roman_wfi_mask_0078.asdf',
                    'roman_wfi_photom_0056.asdf',
                    'roman_wfi_readnoise_0174.asdf',
                    'roman_wfi_saturation_0106.asdf'
                ]
            ]
        }
        assert refs == expected_result
from pytest import mark
import os
import subprocess
import pathlib
from crds.core import heavy_client
from crds.core.exceptions import CrdsLookupError


@mark.roman
def test_getreferences_with_valid_header_ISOT_fmt(roman_test_cache_state):
    """ test_getreferences_with_valid_header: test satisfies Roman 303.1 and 628.1
    """
    roman_test_cache_state.mode = 'local'
    roman_test_cache_state.config_setup()

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


@mark.roman
def test_getreferences_with_valid_header_ISO_fmt(roman_test_cache_state):
    """ test_getreferences_with_valid_header: test satisfies Roman 303.1 and 628.1
    """
    roman_test_cache_state.mode = 'local'
    roman_test_cache_state.config_setup()
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


@mark.roman
def test_getreferences_with_invalid_header(roman_test_cache_state):
    """ test_getreferences_with_invalid_header: test satisfies Roman 303.1
    """
    roman_test_cache_state.mode = 'local'
    roman_test_cache_state.config_setup()
    try:
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
    except CrdsLookupError:
        assert True


def test_wfi_epsf_level3_header_conversions(roman_test_cache_state):
    """Tests retrieving Useafter-relevant keyword from L3 dataset headers and converting to ISOT via precondition hook in the empirical point spread function rmap."""
    roman_test_cache_state.mode = 'local'
    roman_test_cache_state.config_setup()
    header_dict = {
            "ROMAN.META.BASIC.INSTRUMENT": "WFI",
            "ROMAN.META.BASIC.OPTICAL_ELEMENT": "F158",
    }
    test_keys = ['BASIC.TIME_FIRST_MJD', 'BASIC.TIME_MEAN_MJD', 'COADD_INFO.TIME_MEAN']
    for t in test_keys:
        header_dict.update({'ROMAN.META.'+t:60857})
        result = heavy_client.getreferences(
            header_dict,
            observatory="roman",
            context="roman_0007.pmap",
            reftypes=["epsf"]
        )
        assert os.path.basename(result['epsf']) == 'roman_wfi_epsf_0001.asdf'
        del header_dict['ROMAN.META.'+t]


@mark.roman
def test_list_references(roman_test_cache_state):
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
    results, _ = p.communicate()
    results = results.decode('ascii').split("\n")

    assert {item for item in results if item} == expected_result
    
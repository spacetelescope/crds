from pytest import mark
from moto import mock_aws
import boto3
import os
import subprocess
import pathlib
from crds.core import heavy_client, config, log
from crds.core.exceptions import CrdsLookupError
import logging
log.THE_LOGGER.logger.propagate=True
log.set_verbose(50)


REFHEADERS = dict(
    dark={
        "ROMAN.META.INSTRUMENT.NAME": "WFI",
        "ROMAN.META.INSTRUMENT.DETECTOR": "WFI01",
        "ROMAN.META.EXPOSURE.TYPE": "WFI_IMAGE",
        "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01 00:00:00"
    },
    flat={
        "ROMAN.META.INSTRUMENT.NAME": "WFI",
        "ROMAN.META.INSTRUMENT.DETECTOR": "WFI01",
        "ROMAN.META.EXPOSURE.TYPE": "WFI_GRISM",
        "ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT": "GRISM",
        "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01T00:00:00"
    },
    distortion={
        "ROMAN.META.INSTRUMENT.NAME": "WFI",
        "ROMAN.META.INSTRUMENT.DETECTOR": "WFI01",
        "ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT": "F213",
        "ROMAN.META.EXPOSURE.START_TIME": "2020-02-01T00:00:00"
    }
)

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
    expected=dict(
        dark="roman_wfi_dark_0001.asdf", 
        flat="roman_wfi_flat_0004.asdf", 
        distortion="roman_wfi_distortion_0001.asdf"
    )
    for reftype, header in REFHEADERS.items():
        result = heavy_client.getreferences(
            header,
            observatory="roman",
            context="roman_0005.pmap",
            reftypes=[reftype]
        )
        assert pathlib.Path(result[reftype]).name == expected[reftype]

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


@mark.sync
@mark.s3
@mark.roman
@mock_aws
def test_sync_s3_roman_mappings(roman_s3_bucket, roman_temp_cache_state, caplog):
    s3_client = boto3.client("s3", endpoint_url="http://127.0.0.1:5000")
    bucket_name = roman_s3_bucket
    assert config.S3_ENABLED.get() is True
    with mock_aws():
        from crds.sync import SyncScript
        with caplog.at_level(logging.DEBUG, logger="CRDS"):
            errors = SyncScript("crds.sync --last 1")()
            out = caplog.text
        assert "Syncing 30 files" in out
        assert errors == 0


@mark.sync
@mark.s3
@mark.roman
@mock_aws
def test_sync_s3_roman_test_cache(roman_s3_test_bucket, roman_temp_cache_state, caplog):
    s3_client = boto3.client("s3", endpoint_url="http://127.0.0.1:5000")
    bucket_name = roman_s3_test_bucket
    assert config.S3_ENABLED.get() is True
    with mock_aws():
        from crds.sync import SyncScript
        with caplog.at_level(logging.DEBUG, logger="CRDS"):
            errors = SyncScript("crds.sync --contexts roman_0006.pmap")()
            out = caplog.text
        assert "Syncing 6 files" in out
        assert errors == 0


@mark.bestrefs
@mark.s3
@mark.roman
@mock_aws
def test_getreferences_s3_test_cache(roman_s3_test_bucket, roman_temp_cache_state):
    s3_client = boto3.client("s3", endpoint_url="http://127.0.0.1:5000")
    bucket_name = roman_s3_test_bucket
    assert config.S3_ENABLED.get() is True
    with mock_aws():
        for reftype, header in REFHEADERS.items():
            result = heavy_client.getreferences(
                header,
                observatory="roman",
                context="roman_0006.pmap",
                reftypes=[reftype]
            )
            refpath = pathlib.Path(result[reftype])
            assert os.path.exists(refpath)
            assert refpath.name.startswith(f"roman_wfi_{reftype}_")

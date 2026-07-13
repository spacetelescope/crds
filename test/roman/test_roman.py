from pytest import mark, fixture
from moto import mock_aws
import os
import subprocess
import pathlib
from crds.core import heavy_client, config, log
from crds.core.exceptions import CrdsLookupError
import shutil
import glob
import logging
log.THE_LOGGER.logger.propagate=True
log.set_verbose(50)

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


@fixture(scope="function")
def mock_s3_bucket2(s3, roman_s3_cache_state):
    s3.create_bucket(Bucket="stpubdata-mock")
    # setup: upload S3 objects to the mocked S3 bucket
    mappings =['roman_0055.pmap',
    'roman_wfi_0053.imap',
    'roman_wfi_absflux_0001.rmap',
    'roman_wfi_abvegaoffset_0002.rmap',
    'roman_wfi_apcorr_0003.rmap',
    'roman_wfi_area_0002.rmap',
    'roman_wfi_dark_0007.rmap',
    'roman_wfi_darkdecaysignal_0002.rmap',
    'roman_wfi_detectorstatus_0002.rmap',
    'roman_wfi_distortion_0002.rmap',
    'roman_wfi_dustmap_0003.rmap',
    'roman_wfi_epsf_0004.rmap',
    'roman_wfi_etc_0002.rmap',
    'roman_wfi_flat_0006.rmap',
    'roman_wfi_gain_0003.rmap',
    'roman_wfi_integralnonlinearity_0002.rmap',
    'roman_wfi_inverselinearity_0005.rmap',
    'roman_wfi_ipc_0003.rmap',
    'roman_wfi_linearity_0005.rmap',
    'roman_wfi_mask_0003.rmap',
    'roman_wfi_matable_0004.rmap',
    'roman_wfi_optmodel_0001.rmap',
    'roman_wfi_photom_0004.rmap',
    'roman_wfi_readnoise_0005.rmap',
    'roman_wfi_refpix_0003.rmap',
    'roman_wfi_relflux_0001.rmap',
    'roman_wfi_saturation_0003.rmap',
    'roman_wfi_sflat_0001.rmap',
    'roman_wfi_skycells_0002.rmap',
    'roman_wfi_specpsf_0001.rmap']
    for mapping in mappings:
        fpath = config.locate_file(mapping, "roman")
        with open(fpath, 'rb') as f:
            s3.put_object(Bucket="stpubdata-mock", Key=f"roman/crds/mappings/roman/{mapping}", Body=f.read())
        # sync config
    cfg_path = config.locate_file("server_config", "roman")
    with open(cfg_path, 'rb') as f:
        s3.put_object(Bucket="stpubdata-mock", Key=f"roman/crds/config/roman/{os.path.basename(cfg_path)}", Body=f.read())

@mark.sync
@mark.s3
@mark.roman
@mock_aws
def test_sync_s3_roman_mappings(s3, mock_s3_bucket2, roman_s3_cache_state, test_temp_dir, caplog):
    # temp remove one mapping
    from crds.sync import SyncScript
    mappath = os.path.join(roman_s3_cache_state.cache, "mappings", "roman")
    single_map = sorted(glob.glob(f"{mappath}/roman_wfi_skycells*"))[-1] # get the highest version of a random rmap type
    moved = os.path.join(test_temp_dir, os.path.basename(single_map))
    shutil.move(single_map, moved) # temporarily move it out of the cache to simulate a missing mapping
    assert not os.path.exists(single_map)
    with caplog.at_level(logging.INFO, logger="CRDS"):
        errors = SyncScript("crds.sync --last 1")()
        out = caplog.text
    assert "Syncing 1 files" in out
    assert errors == 0
    assert os.path.exists(single_map), shutil.move(moved, single_map) # restore the mapping if the test fails


@mark.sync
@mark.roman
@mark.s3
@mock_aws
def test_sync_s3_roman_mappings_ignore_cache(s3, mock_s3_bucket, roman_s3_cache_state, caplog):
    roman_s3_cache_state.config_setup(**dict(AWS_ACCESS_KEY_ID="test",AWS_SECRET_ACCESS_KEY="test", AWS_SESSION_TOKEN="test", AWS_DEFAULT_REGION="us-east-1"))
    from crds.sync import SyncScript
    with caplog.at_level(logging.DEBUG, logger="CRDS"):
        errors = SyncScript("crds.sync --contexts roman_0055.pmap --ignore-cache")()
        out = caplog.text
    assert errors == 0

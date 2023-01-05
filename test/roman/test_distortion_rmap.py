import os
from pathlib import Path

import pytest


@pytest.mark.distortion
@pytest.mark.roman
def test_distortion_rmap_exists():
    assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "specs" / "wfi_distortion.rmap")


@pytest.mark.distortion
@pytest.mark.roman
def test_distortion_tpn_exist():
    assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_distortion.tpn")


@pytest.mark.distortion
@pytest.mark.roman
def test_distortion_tpn_headers_match_spec():
    """
    TODO: get spec headers from authoritative source
    """
    expected_headers = [
        'ROMAN.META.INSTRUMENT.DETECTOR',
        'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT'
    ]
    with open(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_distortion.tpn", 'r') as distortion_tpn:
        lines = [line.replace('\n', '') for line in distortion_tpn.readlines()]

        headers = [s[:s.index(" ")] for s in filter(
            lambda l: l != '' and l[0] != '#',
            lines
        )]
        assert expected_headers == headers


@pytest.mark.distortion
@pytest.mark.roman
def test_distortion_key_in_combined_spec(combined_spec):
    assert 'distortion' in combined_spec['wfi']

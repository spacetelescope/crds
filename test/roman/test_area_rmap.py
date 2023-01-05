import os
from pathlib import Path

import pytest


@pytest.mark.roman
def test_area_rmap_exists():
    assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "specs" / "wfi_area.rmap")


@pytest.mark.roman
def test_area_tpn_exist():
    assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_area.tpn")


@pytest.mark.roman
def test_area_tpn_headers_match_spec():
    """
    TODO: get spec headers from authoritative source
    """
    expected_headers = [
        'ROMAN.META.INSTRUMENT.DETECTOR',
    ]
    with open(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_area.tpn", 'r') as area_tpn:
        lines = [line.replace('\n', '') for line in area_tpn.readlines()]

        headers = [s[:s.index(" ")] for s in filter(
            lambda l: l != '' and l[0] != '#',
            lines
        )]
        assert expected_headers == headers


@pytest.mark.roman
def test_area_key_in_combined_spec(combined_spec):
    assert 'area' in combined_spec['wfi']

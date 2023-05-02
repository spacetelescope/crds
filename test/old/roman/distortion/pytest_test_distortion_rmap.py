import os

from pathlib import Path

from pytest import mark

@mark.distortion
@mark.roman
class DistortionPyTests:

    def pytest_test_distortion_rmap_exists(self):
        """ A simple pytest to confirm that the distortion rmap exits
        """

        assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "specs" / "wfi_distortion.rmap")

    def pytest_test_distortion_tpn_exist(self):
        """ A simple pytest to confirm that the distortion tpn exists
        """

        assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_distortion.tpn")

    def pytest_test_distortion_tpn_headers(self):
        """ A simple pytest to check the headers in the tpn match the spec

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

    def pytest_test_distortion_key_in_combined_spec(self, combined_spec):
        """ A simple pytest to verify that distortion was added to the combined spec

        :param combined_spec: A session scoped fixture version of the combined spec file
        :type combined_spec: json
        """
        assert 'distortion' in combined_spec['wfi']

import os

from pathlib import Path

from pytest import mark


@mark.roman
class PixelAreaPyTests:

    def pytest_test_pixelarea_rmap_exists(self):
        """ A simple pytest to confirm that the pixelarea rmap exits
        """

        assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "specs" / "wfi_pixelarea.rmap")

    def pytest_test_pixelarea_tpn_exist(self):
        """ A simple pytest to confirm that the pixelarea tpn exists
        """

        assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_pixelarea.tpn")

    def pytest_test_pixelarea_tpn_headers(self):
        """ A simple pytest to check the headers in the tpn match the spec

            TODO: get spec headers from authoritative source
        """
        expected_headers = [
            'ROMAN.META.INSTRUMENT.DETECTOR',
            'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT',
        ]
        with open(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_pixelarea.tpn", 'r') as pixelarea_tpn:
            lines = [line.replace('\n', '') for line in pixelarea_tpn.readlines()]

            headers = [s[:s.index(" ")] for s in filter(
                lambda l: l != '' and l[0] != '#',
                lines
            )]
            assert expected_headers == headers

    def pytest_test_pixelarea_key_in_combined_spec(self, combined_spec):
        """ A simple pytest to verify that pixelarea was added to the combined spec

        :param combined_spec: A session scoped fixture version of the combined spec file
        :type combined_spec: json
        """
        assert 'pixelarea' in combined_spec['wfi']

import os

from pathlib import Path

from pytest import mark


@mark.roman
class PhotomPyTests:

    def pytest_test_photom_rmap_exists(self):
        """ A simple pytest to confirm that the photom rmap exits
        """

        assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "specs" / "wfi_photom.rmap")

    def pytest_test_photom_tpn_exist(self):
        """ A simple pytest to confirm that the photom tpn exists
        """

        assert os.path.exists(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_photom.tpn")

    def pytest_test_photom_tpn_headers(self):
        """ A simple pytest to check the headers in the tpn match the spec

            TODO: get spec headers from authoritative source
        """
        expected_headers = [
            'ROMAN.META.INSTRUMENT.DETECTOR'
        ]
        with open(Path(__file__).parents[3] / "crds" / "roman" / "tpns" / "wfi_photom.tpn", 'r') as photom_tpn:
            lines = [line.replace('\n', '') for line in photom_tpn.readlines()]

            headers = [s[:s.index(" ")] for s in filter(
                lambda l: l != '' and l[0] != '#',
                lines
            )]
            assert expected_headers == headers

    def pytest_test_photom_key_in_combined_spec(self, combined_spec):
        """ A simple pytest to verify that photom was added to the combined spec

        :param combined_spec: A session scoped fixture version of the combined spec file
        :type combined_spec: json
        """
        assert 'photom' in combined_spec['wfi']

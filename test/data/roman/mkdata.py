"""Make test data

To keep up with Roman datamodel changes, the test data need to be updated regularly.

Execute with

    $ cd <this folder>
    $ python -m mkdata
"""
import os

import roman_datamodels as rdm
import roman_datamodels.maker_utils as mu


def mkdata():
    """Create FlatRefModels with various bad settings"""

    # Good model
    flatref = mu.mk_datamodel(rdm.datamodels.FlatRefModel, shape=(2, 2),
                              meta={'instrument': {'name': 'WFI', 'detector': 'WFI16', 'optical_element': 'F158'}})
    flatref.save('roman_wfi16_f158_flat_small.asdf')
    flatrefgrism = mu.mk_datamodel(rdm.datamodels.FlatRefModel, shape=(2, 2),
                              meta={'instrument': {'name': 'WFI', 'detector': 'WFI16', 'optical_element': 'GRISM'}})
    flatrefgrism.save('roman_wfi16_grism_flat_small.asdf')

    # Turn off validations so we can make bad decisions
    os.environ['ROMAN_VALIDATE'] = 'false'

    # Bad reftype
    bad = flatref.copy()
    bad.meta.reftype = 'badtype'
    bad.save('roman_wfi16_f158_flat_badtype.asdf')

    # Invalid schema
    bad = flatref.copy()
    bad.meta.useafter = "yesterday"
    bad.save('roman_wfi16_f158_flat_invalid_schema.asdf')
    bad = flatrefgrism.copy()
    bad.meta.useafter = "yesterday"
    bad.save('roman_wfi16_grism_flat_invalid_schema.asdf')

    # Invalid TPN. Really just another bad schema choice.
    bad = flatref.copy()
    bad.meta.instrument.optical_element = 'BAD'
    bad.save('roman_wfi16_f158_flat_invalid_tpn.asdf')
    bad = flatrefgrism.copy()
    bad.meta.instrument.optical_element = 'BAD'
    bad.save('roman_wfi16_grism_flat_invalid_tpn.asdf')

if __name__ == '__main__':
    mkdata()

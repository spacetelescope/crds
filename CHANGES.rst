11.10.0 (2022-03-25)
====================

HST
---

- Add V3 of ACS precondition header hook. [#864]

11.9.0 (2022-02-23)
===================

Roman
-----

- corrected area rmap to match updates to schema [#863]

HST
---

- Add LITREF check to tpns for synphot component files. [#862]

11.8.0 (2022-02-15)
===================

Roman
-----

- New PixelArea RefType + PyTests. [#861]

11.7.0 (2022-02-09)
===================

Roman
-----

- New Photom RefType + PyTests. [#860]

11.6.1 (2022-02-07)
===================

JWST
----

- Add pub to the possible submission groups. [#859]

11.6.0 (2022-01-13)
===================

JWST
----

- Update submission urls to include jwst-crds-pub [#856]

- Fix syntax in all_tpn affecting readpatt verification [#857]

Infrastructure
--------------

-  Update minimum python to 3.8 [#858]

11.5.2 (2021-12-10)
===================

Roman
-----

- Trim translations to be specific to roman [#854]

11.5.1 (Unreleased)
===================

JWST
----

- Update miri pathloss spec [#855]

Infrastructure
--------------

- Update documentation for the Submission API [#853]

11.5.0 (2021-10-28)
===================

JWST
----

- Add new reftype fringefreq [#846]

Roman
-----

- Added new reftype saturation            [#847]

- Changed dark reftype definition         [#852]

- Changed readnoise reftype definition    [#851]

11.4.3 (2021-09-30)
===================

JWST
----

- Change JWST validation errors into warnings. [#845]

11.4.2 (2021-09-20)
===================

HST
---

- Update STIS and ACS IMPHTTAB validations to permit additional
  values in the DATACOL column. [#844]

11.4.1 (2021-09-15)
===================

JWST
----

- Update JWST certifier to show all datamodels validation failures
  instead of stopping at the first. [#842]

Infrastructure
--------------

- Switch to setuptools_scm for package version management and
  deprecate ``crds.__rationale__`` variable. [#843]

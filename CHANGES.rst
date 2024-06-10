11.17.24 (20204-06-10)
=====================

JWST
----
- Added pars-darkcurrentstep rmaps for NIRISS, NIRCAM and NIRSPEC [#1045]

11.17.23 (2024-06-03)
=====================

JWST
----
- Added RMAPS for miri_pars-spectralleakstep and nirspec_pars-nsleanstep
- Added GRATING as selection for nirspec_dark.spec and nirspec_pars-nscleanstep.rmap [#1043]

11.17.22 (2024-05-09)
=====================

HST
---

- Added RMAP and TPN files for new COS HVDSTAB reference file [#1042]
- Fix for acs imphttab ref file submission failures [#1044]

JWST
----
- Added several RMAPS for pars-resamplestep/specstep [#1038]


11.17.21 (2024-04-30)
=====================

ROMAN
-----

- Added support for pars- reference files [#1036]

General
-------

- Use try/except for np.float128 import [#1037]


11.17.20 (2024-04-18)
=====================

ROMAN
-----
- Added `metrics_logger` decorator to Roman tests delivered with older builds [#1034]

TESTING / AUTOMATION
--------------------
- Pytest configuration changes to address ongoing test suite failures, marked individual tests with their respective observatory [#1034]


11.17.19 (2024-02-22)
=====================

JWST
----
-Added MODEL to be a PEDIGREE option for JWST. [#1032]

- Formalize the stale-by-context report tool [#1039]

11.17.18 (2024-02-21)
=====================

JWST
----
-Added new rmap for MIRI pars-emicorrstep. [#1030]

11.17.17 (2024-02-20)
=====================

JWST
----
-Added new rmap for NIRISS nrm. [#1027]
-Added new rmap for NIRSPEC drizpars. [#1028]
-Added new rmap for NIRISS pars-whitelightstep. [#1029]


11.17.16 (2024-02-05)
=====================

JWST
----
- Added new rmap for miri_pars-pixelreplacestep [#1025]

General
-------
- Fixed issue with releases and CHANGES.rst [#1026]

11.17.15 (2024-01-22)
=====================

JWST
----
- Added new rmap for miri_mask [#1020]

General
-------

- for the test caching CI workflow (``.github/workflows/cache.yml``), explicitly checkout CRDS to enable reuse in other repositories' CI [#1022]

11.17.14 (2023-12-14)
=====================

General
-------

- Remove jwst pub and add roman tvac to submission list. [#1018]
- Replaced deprecated ``ast.Str`` with ``ast.Constant`` [#1007]

HST
---

- Add n/a to components of the cos badttab reftype [#1019]

11.17.13 (2023-12-01)
====================

JWST
----
-Removed constraints in nirspec_pathloss.tpn. [#1017]

11.17.12 (2023-11-29)
====================

JWST
----
-Fixed value of suffix in rmap for miri_emicorr. [#1016]


11.17.11 (2023-11-28)
====================

JWST
----
-Fixed value of filetype in rmap for miri_emicorr. [#1015]


11.17.10 (2023-11-14)
====================

JWST
----
- Added PIXAR_SR and PIXAR_A2 to miri photom tpn. [#1013]
- Added new rmap for miri.emicorr. [#1014]


11.17.9 (2023-11-08)
====================

General
-------

- bugfix: get observatory metadata inside asdf file handler [#1012]


11.17.8 (2023-11-07)
====================

General
-------

- Update tests for expected output with asdf 3.0+ [#1004]

- Downgrade unhandled name in crds.io.naming.newer from an error to a warning [#1008]

- Add setval() and getval() methods to crds.io.asdf.AsdfFile class [#1009]


Documentation
-------------

- Added documentation on how to search for and download bestrefs by dataset ID programatically [#1001]

JWST
----
- Added Filter and Subarray to miri_pars-jumpstep.rmap [#1010]
- Added BAND to miri_gain and DETECTOR to miri_pars-detector1pipeline spec files. [#1011]


11.17.7 (2023-10-20)
====================

General
-------

- Replaced deprecated np.product with np.prod in crds.certify.validators.core [#975]

- Remove "lxml" from submission optional dependencies [#999]

Testing
-------

- Migrated test suite from nose to pytest, running CI tests for python 3.9, 3.10, 3.11 [#998]


11.17.6 (2023-09-08)
=====================

JWST
----

- Added a substitution to miri_ipc [#958]

11.17.5 (2023-09-07)
=====================

JWST
----

- Added new rmap nirspec outlier detection [#950]
- Added new rmap miri Interpixel Capacitance [#954]
- Added CHANNEL to parkeys for miri_apcorr.rmap [#955]
- Added new rmap niriss charge_migration step [#956] 

11.17.4 (2023-08-28)
=====================

JWST
----

- Added new rmap miri gain [#945]

11.17.3 (2023-08-17)
====================

ROMAN
-----

- Added metrics-logger decorators with DMS tags to appropriate Roman tests [#943]

11.17.2 (2023-06-29)
====================

HST
---

- Added WFC3 SATUFILE new reference file [#941]

11.17.1 (2023-06-20)
=====================

General
-------

- Removed python 3.8 check from ci.yml [#934]

- Removed references to ICD-47 in users guide [#936]

- translate 'ANY' as equal to '*' when selecting match rules in rmap changes. Prevents equal weight special case errors from occurring unnecessarily [#939]

-  Refactor setup_test_cache to allow for simply updating local cache [#966]

JWST
----

- Switch jwst DATAMODEL to jwst.datamodels.JwstDataModel [#938]

11.17.0 (2023-04-21)
===================

Roman
-----

- Replace W146 with F146 [#932]


11.16.22 (2023-04-11)
=====================

General
-------

- Replace ``lxml`` dependency with ``BeautifulSoup`` for submission/login html error parsing [#926]

JWST
----

- Added stale archive report core code [#928]

- Update miri pars-jumpstep parkeys [#931]

11.16.21 (2023-03-09)
=====================

Roman
-----

- Added new rmap WFI Reference Pixels [#924]

General
-------

- Replace deprecated import ``pkg_resources`` with ``packaging.requirements``. [#923]

11.16.20 (2023-01-31)
=====================

Roman
-----

- Added new rmap WFI Inverse Linearity [#920]


11.16.19 (2023-01-17)
=====================

Roman
-----

- Added new reference file type: IPC Kernel [#918]


11.16.18 (2023-01-05)
=====================

JWST
----

- add SUB400X256ALWB to the NIRCam subarray list [#915]

Roman
-----

- bugfix: getreferences uses get_locator_module to call dataset_to_ref_header [#916]

- bestrefs calls ``dataset_to_ref_header`` outside of the "fast" condition. Header translation for Roman will occur regardless of the "fast" arg (which can sometimes be determined by the logging verbosity level). [#917]


11.16.17 (2022-12-30)
=====================

Roman
-----

- Dataset to Ref header key matching where "roman" prefix is missing [#910]  

General
-------
- exclude build/ and install.log from source control [#907]

- update versions in github actions workflows [#914]

JWST
----

- Add subarray to the miri filteroffset spec [#908]

- Initial spec implementations for pars-jumpstep for miri, nircam, and nirspec [#909]

- Add new reftypes pars-residualfringestep and pars-undersamplecorrectionstep [#911]

- Add (260, 2048) as a valid size for nirspec saturation [#912]


11.16.16 (2022-11-04)
=====================

HST
---

- Affected datasets script sets BIASFILE bestref to N/A when specific conditions are met for ACS WFC datasets (CCDGAIN=0.5 or 1.4) [#906]

General
-------
- Don't issue warning in ``crds sync`` for files with status "delivered" [#903]

- Documentation minor updates: command_line_tools, programmatic_interface [#905]


11.16.15 (2022-10-20)
=====================

Roman
-----
- Automatic confirmation for roman pipeline reference file submissions [#904]

11.16.14 (2022-09-22)
=====================

General
-------
- Equal Weight Special Case log messages include filenames and useafter dates [#901]

11.16.13 (2022-09-20)
=====================

General
-------

- Updated README to reference ``stenv`` [#899]

HST
---

- Reversion: "equal weight special case" generates a warning instead of error for HST [#898]

11.16.12 (2022-09-12)
=====================

General
-------

- File submission object includes 'file_map' dictionary attribute of uploaded and renamed filenames [#897]

11.16.11 (2022-09-08)
=====================

JWST
----

- Add LAMP_MODE and LAMP_STATE to NIRSpec SFLAT spec [#896]

11.16.10 (2022-09-02)
=====================

JWST
----

- Update nirspec fflat specs [#895]

11.16.9 (2022-08-18)
====================

General
-------

- User Guide updates: mission-based tabs for code examples, Roman content added [#894]

11.16.8 (2022-08-09)
====================

Roman
-----

- Allow variation in reftype naming convention for ASDF validation checks in crds.certify [#893]


11.16.7 (2022-08-02)
====================

General
-------

- Changed "equal weight special case" warning to an error [#892]

- Revised core.utils to allow I/O to work under Windows [#891]


11.16.6 (2022-07-18)
====================

JWST
----

-  update niriss pars-jumpstep parkeys [#890]


11.16.5 (2022-06-27)
====================

General
-------

- Updated GH action release token [#889]

Roman
-----

- Useafter string reformats with space instead of "T" between date and time [#888]


11.16.4 (2022-06-22)
====================

- Update the timeout for RPC calls [#887]

11.16.3 (2022-06-15)
====================

General
-------

- Allow forward slash and equals signs in Reason for Delivery [#886]


11.16.2 (2022-06-09)
====================

Roman
-----

- added ref-rmap header translation for p_optical_element, updated tests [#885]


11.16.1 (2022-06-06)
====================

General
-------

- Hotfix for API character validation with more thorough testing added [#884]


11.16.0 (2022-05-27)
====================

General
-------

- Minor bugfix checks for invalid (special) chars in "reason for delivery" text submitted via programmatic api [#882]

JWST
----

- Update and add specs for all instruments for reftype pars-rampfitstep. [#883]

11.15.0 (2022-05-23)
====================

General
-------

- Manually added release date for previous release [#881]

JWST
----

- Added new rmap for NIRISS filteroffset [#881]

HST
---

- Add substitutions for HST ACS to support biasfile selection [#880]


11.14.0 (2022-05-05)
====================

Roman
-----
- Added top-level tag validation for roman asdf [#878]

JWST
----

- Add back pars-masterbackgroundnrsslitsstep in the jwst specs [#879]


11.13.1 (2022-04-26)
====================

Roman
-----
- move MA_TABLE_NUMBER WFI dark rmap parkey from observation to exposure [#877]


11.13.0 (2022-04-22)
====================

JWST
----

- Create new reftype mrsptcorr [#875]

- add new reftype mrsxartcorr [#874]

- Update miri pars-spec2pipeline for exp_type addition to parkeys [#873]

- Add spec for new pars-wfsscontamstep [#872]

- Update parkeys for NIRSpec/NIRISS pars-spec2pipeline [#871]

- Rename MasterBackgroundNrsSlitsStep pars files to MasterBackgroundMosStep [#870]

Roman
-----

- update parkeys for WFI dark references [#868]
- useafter based on exposure.start_time instead of observation.date, observation.time [#876]

11.12.1 (2022-04-14)
====================

General
-------

- Implement timeout on CRDS Server network requests [#869]

11.12.0 (2022-03-31)
====================

Roman
-----

- added: distortion rmap + tpn [#867]


11.11.0 (unreleased)
====================

JWST
----

- update parkeys for NIRSpec apcorr and extract1d references [#866]

11.10.1 (2022-03-26)
====================

Infrastructure
--------------

- Fix bug in script where bash syntax was used with /bin/sh. [#865]


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

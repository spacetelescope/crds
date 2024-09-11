<!-- If this PR closes a JIRA ticket, make sure the title starts with the JIRA issue number,
for example JP-1234: <Fix a bug> -->
Resolves [CCD-nnnn](https://jira.stsci.edu/browse/CCD-nnnn)

<!-- If this PR closes a GitHub issue, reference it here by its number -->
Closes #

<!-- describe the changes comprising this PR here -->
This PR addresses ...

<!-- if you can't perform these tasks due to permissions, please ask a maintainer to do them -->
## Tasks
- [ ] update or add relevant tests
- [ ] update relevant docstrings and / or `docs/` page
- [ ] Does this PR change any API used downstream? (if not, label with `no-changelog-entry-needed`)
  - [ ] write news fragment(s) in `changes/`: `echo "changed something" > changes/<PR#>.<changetype>.rst` (see below for change types)

<details><summary>news fragment change types...</summary>

- ``changes/<PR#>.hst.rst``: HST reference files
- ``changes/<PR#>.jwst.rst``: JWST reference files
- ``changes/<PR#>.roman.rst``: Roman reference files
- ``changes/<PR#>.doc.rst``: documentation change
- ``changes/<PR#>.testing.rst``: change to tests or test automation
- ``changes/<PR#>.general.rst``: infrastructure or miscellaneous change
</details>


# 8 - TSOVISIT + LAMP
.....................

Technically a couple of other updates should or will need to be made in the
near future, but they get more complicated than what the current scheme
allows. For example, right now the section that maps pipeline cfgs to lists of
EXP_TYPEs doesn't actually work 100% correctly for some of the modes, like
TSO. This is due to the fact that TSO is now an option (can be toggled on/off)
in the APT for several modes, such as MIRI imaging and NIRISS SOSS. Until
recently NIS_SOSS had been considered to always be TSO, but now it is in fact
optional. Same thing with MIR_IMAGE: up until now it's been considered to
always be NON-TSO, but now (or soon will be) optional. But the EXP_TYPE value
remains the same; you have to key off of another item to tell if it's TSO (the
TSOVISIT keyword). So this means the logic will need to be enhanced to look at
both EXP_TYPE and TSOVISIT in order to determine which pipeline cfg is
appropriate.

The same is true of another new level-2b cfg that we implemented recently:
calwebb_nrslamp-spec2.cfg. It gets applied to exposures that have a certain
EXP_TYPE and LAMP value, so you again need to key off of two items (not just
EXP_TYPE).

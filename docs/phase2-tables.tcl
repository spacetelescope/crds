## -*- Mode: tcl -*-

#
proc Load_Rel_Constr_Forms_SM4Test {} {
# This is an attempt at representing the phase 2 proposal instructions
# using the phase 2 Syntax.

### Note: -Availability 
###  Blank == Supported mode.  "caut-use" == Available mode.  "eng-only" == Restricted mode

#
# Instrument definitions
#
Instrument {-Name "WFPC2"}
Instrument {-Name "WFC3"  -Pure_Par_Allowed 1}
Instrument {-Name "FGS"}
Instrument {-Name "COS"}
Instrument {-Name "S/C" -Availability "caut-use"}
Instrument {-Name "NICMOS" -Availability "eng-only"}
Instrument {-Name "STIS"}
Instrument {-Name "ACS" -Pure_Par_Allowed 1}

#
# Calibration targets
#
Calibration_Target {-Name "DARK" -Instrument {"S/C"}}
Calibration_Target {-Name "DARK" -Instrument {"FGS"}            -Availability "caut-use"}
Calibration_Target {-Name "DARK" -Instrument {"WFPC2" "NICMOS"} -Availability "caut-use" -Pure_Par_Allowed 1}
Calibration_Target {-Name "DARK" -Instrument {"STIS" "ACS"}     -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "DARK" -Instrument {"WFC3" "COS"}     -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "DARK-NM" -Instrument {"WFC3"}     -Availability "eng-only" -Pure_Par_Allowed 1}

Calibration_Target {-Name "WAVE" -Instrument {"STIS" "COS"} -Pure_Par_Allowed 1}

Calibration_Target {-Name "INTFLAT" -Instrument "WFPC2" -Availability "caut-use" -Pure_Par_Allowed 1}

Calibration_Target {-Name "KSPOTS" -Instrument {"WFPC2"} -Availability "caut-use" -Pure_Par_Allowed 1}

Calibration_Target {-Name "BIAS" -Instrument {"STIS"}  -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "BIAS" -Instrument {"ACS"}   -Availability "caut-use" -Pure_Par_Allowed 1}
Calibration_Target {-Name "BIAS" -Instrument {"WFPC2"} -Availability "caut-use" -Pure_Par_Allowed 1}
Calibration_Target {-Name "BIAS" -Instrument {"WFC3"}  -Availability "caut-use" -Pure_Par_Allowed 1}

Calibration_Target {-Name "UVFLAT" -Instrument "WFPC2" -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "VISFLAT" -Instrument "WFPC2" -Availability "eng-only" -Pure_Par_Allowed 1}

# Leave none calibration target eng-only for non-stis instruments
Calibration_Target {-Name "NONE" -Instrument {"WFPC2" "NICMOS" "ACS"} -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "NONE" -Instrument {"COS" "WFC3"} -Availability "eng-only"}

# Make none calibration target caut-use for stis.
Calibration_Target {-Name "NONE" -Instrument {"STIS"} -Availability "caut-use" -Pure_Par_Allowed 1}


Calibration_Target {-Name "CCDFLAT" -Instrument {"STIS"} -Pure_Par_Allowed 1}

Calibration_Target {-Name "TUNGSTEN" -Instrument {"ACS"} -Availability "eng-only"}
Calibration_Target {-Name "TUNGSTEN" -Instrument {"WFC3"} -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "DEUTERIUM" -Instrument {"ACS"} -Availability "eng-only"}
Calibration_Target {-Name "DEUTERIUM" -Instrument {"WFC3" "COS"} -Availability "eng-only" -Pure_Par_Allowed 1}

Calibration_Target {-Name "DARK-EARTH-CALIB" -Instrument {"WFC3"} -External 1 -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "DARK-EARTH-CALIB" -Instrument {"ACS"} -External 1}
Calibration_Target {-Name "EARTH-CALIB" -Instrument {"WFC3"} -External 1 -Availability "eng-only" -Pure_Par_Allowed 1}
Calibration_Target {-Name "EARTH-CALIB" -Instrument {"WFPC2" "S/C" "FGS" "STIS" "NICMOS" "ACS" "COS"} -External 1}
Calibration_Target {-Name "ANTI-SUN" -Instrument {"WFPC2" "S/C" "FGS" "NICMOS" "STIS" "ACS" "COS" "WFC3"} -External 1}
Calibration_Target {-Name "ORBIT-POLE" -Instrument {"WFPC2" "S/C" "FGS" "NICMOS" "STIS" "ACS" "COS" "WFC3"} -External 1}
Calibration_Target {-Name "ORBIT-POLE-NORTH" -Instrument {"WFPC2" "S/C" "FGS" "NICMOS" "STIS" "ACS" "COS" "WFC3"} -External 1}
Calibration_Target {-Name "ORBIT-POLE-SOUTH" -Instrument {"WFPC2" "S/C" "FGS" "NICMOS" "STIS" "ACS" "COS" "WFC3"} -External 1}
Calibration_Target {-Name "ANY" -Instrument {"WFPC2" "S/C" "FGS" "NICMOS" "STIS" "ACS" "COS" "WFC3"} -External 1 -Pure_Par_Allowed 1}

#######################################################################################
#
# Instrument "WFPC2"
#
#######################################################################################
Print_If_Verbose "WFPC2 forms"
Instrument_Cfg {-Name "WFPC2" -Instrument "WFPC2" -Availability "eng-only"}
Object_Set {-Name "MIRROR-MOTION" -Type "mode"}
Instrument_Mode {-Name "IMAGE" -Instrument "WFPC2" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "DECON" -Instrument "WFPC2" -Availability "eng-only"}
Instrument_Mode {-Name "AFM" -Instrument "WFPC2" -Availability "eng-only"
    -Object_Sets "MIRROR-MOTION"}
Instrument_Mode {-Name "POM" -Instrument "WFPC2" -Availability "eng-only"
    -Object_Sets "MIRROR-MOTION"}

Object_Set {-Name "CCD" -Type "aperture"}
Object_Set {-Name "UNFIXED-CCD" -Type "aperture"}
Object_Set {-Name "FIXED-CCD" -Type "aperture"}
Instrument_Aperture {-Name "PC1" -Instrument "WFPC2" -Object_Sets {"CCD" "UNFIXED-CCD"}}
Instrument_Aperture {-Name "WF2" -Instrument "WFPC2" -Object_Sets {"CCD" "UNFIXED-CCD"}}
Instrument_Aperture {-Name "WF3" -Instrument "WFPC2" -Object_Sets {"CCD" "UNFIXED-CCD"}}
Instrument_Aperture {-Name "WF4" -Instrument "WFPC2" -Object_Sets {"CCD" "UNFIXED-CCD"}}
Instrument_Aperture {-Name "PC1-FIX" -Instrument "WFPC2" -Object_Sets {"CCD" "FIXED-CCD"}}
Instrument_Aperture {-Name "WF2-FIX" -Instrument "WFPC2" -Object_Sets {"CCD" "FIXED-CCD"}}
Instrument_Aperture {-Name "WF3-FIX" -Instrument "WFPC2" -Object_Sets {"CCD" "FIXED-CCD"}}
Instrument_Aperture {-Name "WF4-FIX" -Instrument "WFPC2" -Object_Sets {"CCD" "FIXED-CCD"}}
Instrument_Aperture {-Name "WFALL" -Instrument "WFPC2"}
Instrument_Aperture {-Name "WFALL-FIX" -Instrument "WFPC2"}
Object_Set {-Name "PARTIAL-ROTATION" -Type "aperture"}
Instrument_Aperture {-Name "F160BN15" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "FQCH4N15" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "FQCH4N33" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "FQCH4P15" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "FQCH4W2" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "FQCH4W3" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "FQCH4W4" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "FQUVN33" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "LRF" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "POLQN18" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "POLQN33" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "POLQP15P" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "POLQP15W" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}}
Instrument_Aperture {-Name "F160AN15" -Instrument "WFPC2" -Object_Sets {"PARTIAL-ROTATION"}
                     -Availability "caut-use"}

Instrument_Spectral_Element {-Name "DEF" -Instrument "WFPC2" -Wheel "*"
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "F122M" -Instrument "WFPC2" -Wheel 1}
Instrument_Spectral_Element {-Name "F130LP" -Instrument "WFPC2" -Wheel 2}
Instrument_Spectral_Element {-Name "F160AW" -Instrument "WFPC2" -Wheel 1}
Instrument_Spectral_Element {-Name "F160AN15" -Instrument "WFPC2" -Wheel 1
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "F160AP15" -Instrument "WFPC2" -Wheel 1
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "F160BW" -Instrument "WFPC2" -Wheel 1}
Instrument_Spectral_Element {-Name "F160BP15" -Instrument "WFPC2" -Wheel 1
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "F160BN15" -Instrument "WFPC2" -Wheel 1}
Instrument_Spectral_Element {-Name "F165LP" -Instrument "WFPC2" -Wheel 2}
Instrument_Spectral_Element {-Name "F170W" -Instrument "WFPC2" -Wheel 8}
Instrument_Spectral_Element {-Name "F185W" -Instrument "WFPC2" -Wheel 8}
Instrument_Spectral_Element {-Name "F218W" -Instrument "WFPC2" -Wheel 8}
Instrument_Spectral_Element {-Name "F255W" -Instrument "WFPC2" -Wheel 8}
Instrument_Spectral_Element {-Name "F300W" -Instrument "WFPC2" -Wheel 9}
Instrument_Spectral_Element {-Name "F336W" -Instrument "WFPC2" -Wheel 3}
Instrument_Spectral_Element {-Name "F343N" -Instrument "WFPC2" -Wheel 5}
Instrument_Spectral_Element {-Name "F375N" -Instrument "WFPC2" -Wheel 5}
Instrument_Spectral_Element {-Name "F380W" -Instrument "WFPC2" -Wheel 9}
Instrument_Spectral_Element {-Name "F390N" -Instrument "WFPC2" -Wheel 5}
Instrument_Spectral_Element {-Name "F410M" -Instrument "WFPC2" -Wheel 3}
Instrument_Spectral_Element {-Name "F437N" -Instrument "WFPC2" -Wheel 5}
Instrument_Spectral_Element {-Name "F439W" -Instrument "WFPC2" -Wheel 4}
Instrument_Spectral_Element {-Name "F450W" -Instrument "WFPC2" -Wheel 10}
Instrument_Spectral_Element {-Name "F467M" -Instrument "WFPC2" -Wheel 3}
Instrument_Spectral_Element {-Name "F469N" -Instrument "WFPC2" -Wheel 6}
Instrument_Spectral_Element {-Name "F487N" -Instrument "WFPC2" -Wheel 6}
Instrument_Spectral_Element {-Name "F502N" -Instrument "WFPC2" -Wheel 6}
Instrument_Spectral_Element {-Name "F547M" -Instrument "WFPC2" -Wheel 3}
Instrument_Spectral_Element {-Name "F555W" -Instrument "WFPC2" -Wheel 9}
Instrument_Spectral_Element {-Name "F569W" -Instrument "WFPC2" -Wheel 4}
Instrument_Spectral_Element {-Name "F588N" -Instrument "WFPC2" -Wheel 6}
Instrument_Spectral_Element {-Name "F606W" -Instrument "WFPC2" -Wheel 10}
Instrument_Spectral_Element {-Name "F622W" -Instrument "WFPC2" -Wheel 9}
Instrument_Spectral_Element {-Name "F631N" -Instrument "WFPC2" -Wheel 7}
Instrument_Spectral_Element {-Name "F656N" -Instrument "WFPC2" -Wheel 7}
Instrument_Spectral_Element {-Name "F658N" -Instrument "WFPC2" -Wheel 7}
Instrument_Spectral_Element {-Name "F673N" -Instrument "WFPC2" -Wheel 7}
Instrument_Spectral_Element {-Name "F675W" -Instrument "WFPC2" -Wheel 4}
Instrument_Spectral_Element {-Name "F702W" -Instrument "WFPC2" -Wheel 10}
Instrument_Spectral_Element {-Name "F785LP" -Instrument "WFPC2" -Wheel 2}
Instrument_Spectral_Element {-Name "F791W" -Instrument "WFPC2" -Wheel 4}
Instrument_Spectral_Element {-Name "F814W" -Instrument "WFPC2" -Wheel 10}
Instrument_Spectral_Element {-Name "F850LP" -Instrument "WFPC2" -Wheel 2}
Instrument_Spectral_Element {-Name "F953N" -Instrument "WFPC2" -Wheel 1}
Instrument_Spectral_Element {-Name "F1042M" -Instrument "WFPC2" -Wheel 11}
Instrument_Spectral_Element {-Name "FQUVN" -Instrument "WFPC2" -Wheel 11
    -Min_Wave 3765 -Max_Wave 3992}
Instrument_Spectral_Element {-Name "FQUVN33" -Instrument "WFPC2" -Wheel 11
    -Min_Wave 3765 -Max_Wave 3765}
Instrument_Spectral_Element {-Name "FQCH4N" -Instrument "WFPC2" -Wheel 11
    -Min_Wave 5433 -Max_Wave 8929}
Instrument_Spectral_Element {-Name "FQCH4N33" -Instrument "WFPC2" -Wheel 11
    -Min_Wave 6193 -Max_Wave 6193}
Instrument_Spectral_Element {-Name "FQCH4N15" -Instrument "WFPC2" -Wheel 11
    -Min_Wave 6193 -Max_Wave 6193}
Instrument_Spectral_Element {-Name "FQCH4P15" -Instrument "WFPC2" -Wheel 11
    -Min_Wave 8929 -Max_Wave 8929}
Instrument_Spectral_Element {-Name "POLQ" -Instrument "WFPC2" -Wheel 11}
Instrument_Spectral_Element {-Name "POLQN33" -Instrument "WFPC2" -Wheel 11}
Instrument_Spectral_Element {-Name "POLQN18" -Instrument "WFPC2" -Wheel 11}
Instrument_Spectral_Element {-Name "POLQP15" -Instrument "WFPC2" -Wheel 11}
Instrument_Spectral_Element {-Name "LRF" -Instrument "WFPC2" -Wheel 12
    -Min_Wave 3710 -Max_Wave 9762}
Instrument_Spectral_Element {-Name "FR418N" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR418N33" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR418N18" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR533N" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR533N33" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR533N18" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR680N" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR680N33" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR680N18" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR868N" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR868N33" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR868N18" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR418P15" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR533P15" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR680P15" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "FR868P15" -Instrument "WFPC2" -Wheel 12
    -Availability "caut-use"}
Instrument_Spectral_Element {-Name "NONE" -Instrument "WFPC2" -Wheel "*"
    -Availability "caut-use"}

#   .        Follows a list of a lot of spectral elements
#   .
#   .
#Instrument_Spectral_Element {-Name "LRF" -Instrument "WFPC2" -Wheel 12 -Min_Wave 3716
#    -Max_Wave 9785}

Instrument_Optional_Parameter {-Name "ATD-GAIN" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "string" -String_Values {7 15} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "CLOCKS" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "string" -String_Values {"YES" "NO"} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "CR-SPLIT" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "both" -String_Values {"NO" "DEF"} -Min_Val 0.0 -Max_Val 1.0 -Open_Interval "both" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "CR-TOLERANCE" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "numeric" -Min_Val 0.0 -Max_Val 1.0 -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SUM" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "string" -String_Values {"1X1" "2X2"} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "READ" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "string" -String_Values {"1" "2" "3" "4" "1+1" "1+2" "1+3" "1+4" "2+3" "2+4" "3+4"
                                   "1+2+3" "1+2+4" "1+3+4" "2+3+4" "YES" "NO"} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "BLADE" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "string" -String_Values {"A" "B"} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "CLEAR" -Instrument "WFPC2" -Mode "IMAGE"
    -Type "string" -String_Values {"YES" "NO"} -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "POM-X" -Instrument "WFPC2" -Mode "POM"
    -Type "numeric" -Min_Val -900 -Max_Val 900}
Instrument_Optional_Parameter {-Name "POM-Y" -Instrument "WFPC2" -Mode "POM"
    -Type "numeric" -Min_Val -900 -Max_Val 900}
Instrument_Optional_Parameter {-Name "AFM1-X" -Instrument "WFPC2" -Mode "AFM"
    -Type "numeric" -Min_Val -300 -Max_Val 300}
Instrument_Optional_Parameter {-Name "AFM3-X" -Instrument "WFPC2" -Mode "AFM"
    -Type "numeric" -Min_Val -300 -Max_Val 300}
Instrument_Optional_Parameter {-Name "AFM4-X" -Instrument "WFPC2" -Mode "AFM"
    -Type "numeric" -Min_Val -300 -Max_Val 300}
Instrument_Optional_Parameter {-Name "AFM1-Y" -Instrument "WFPC2" -Mode "AFM"
    -Type "numeric" -Min_Val -300 -Max_Val 300}
Instrument_Optional_Parameter {-Name "AFM3-Y" -Instrument "WFPC2" -Mode "AFM"
    -Type "numeric" -Min_Val -300 -Max_Val 300}
Instrument_Optional_Parameter {-Name "AFM4-Y" -Instrument "WFPC2" -Mode "AFM"
    -Type "numeric" -Min_Val -300 -Max_Val 300}


Combination {-Type "legal" -Instrument "WFPC2" -Condition {{"cfg" "WFPC2"}}
    -Result {{"mode" "*"}}}
Combination {-Type "legal" -Instrument "WFPC2" -Condition {{"mode" "IMAGE"}}
    -Result {{"spectral_element" "*"} {"aperture" "*"}}}
Combination {-Type "legal" -Instrument "WFPC2" -Condition {{"mode" "DECON"}}
    -Result {{"spectral_element" {! "*"}} {"aperture" "*"}}}
Combination {-Type "legal" -Instrument "WFPC2" -Condition {{"mode" "MIRROR-MOTION"}}
    -Result {{"spectral_element" {! "*"}} {"aperture" {! "*"}}}}

Combination {-Type "illegal" -Instrument "WFPC2" -Condition
    {{"mode" {! "DECON"}} {"calibration_target" {"BIAS" "DARK" "KSPOTS"}}}
    -Result {{"spectral_element" {! "DEF"}}}
    -Message "WFPC2 filter other than DEF cannot be specified for BIAS, DARK and KSPOTS"}

Combination {-Type "legal" -Instrument "WFPC2" -Condition
    {{"calibration_target" {"INTFLAT" "KSPOTS" "UVFLAT" "VISFLAT"}}}
    -Result {{"exp_time" "DEF"}}}

Combination {-Type "legal" -Instrument "WFPC2"
    -Condition {{"mode" {"AFM" "POM"}}}
    -Result {{"exp_time" "DEF"}}}
Combination {-Type "illegal" -Instrument "WFPC2" -Condition
    {{"calibration_target" "BIAS"}}
    -Result {{"exp_time" {!= 0}}}
    -Message "WFPC2 BIAS must be given an exposure time of zero"}
Combination {-Type "illegal" -Instrument "WFPC2" -Condition
    {{mode "IMAGE"} {{"optional_parameter" "CLOCKS"} "YES"}}
    -Result {{"exp_time" {< "1"}}}
    -Message "WFPC2 exposure time must be greater than 1 second when CLOCKS=YES"}
Combination {-Type "illegal" -Instrument "WFPC2"
    -Condition {{"mode" "IMAGE"}}
    -Result {{{"optional_parameter" "READ"} {! "YES" "NO"}}}
    -Availability "caut-use"
    -Message "WFPC2 READ optional parameter values other than YES or NO are engineering only"}

#
# Added the following constraints in support of OPR 37554
# Frank Tanner - May, 1999
#
Combination {-Type "illegal" -Instrument "WFPC2"
    -Condition {{"spectral_element" "LRF"}}
    -Result {{"aperture" {! "LRF"}}}
    -Message "WFPC2 exposures with LRF as a spectral element must also have LRF as the aperture"}
Combination {-Type "illegal" -Instrument "WFPC2"
    -Condition {{"aperture" "LRF"}}
    -Result {{"spectral_element" {! "LRF"}}}
    -Message "WFPC2 exposures with aperture LRF must also have LRF as a spectral element"}

#
# Added the following constraint in support of OPR 37894
# Frank Tanner - June, 1999
#
Combination {-Type "illegal" -Instrument "WFPC2"
    -Condition {{"mode" {"AFM" "POM"}}}
    -Result {{"calibration_target" {! "NONE"}}}
    -Message "WFPC2 exposures in AFM or POM mode must specify target NONE"}

#######################################################################################
#
# Instrument FGS
#
#######################################################################################
Print_If_Verbose "FGS forms"
Instrument_Cfg {-Name "FGS" -Instrument "FGS"}
Instrument_Mode {-Name "POS" -Instrument "FGS"}
Instrument_Mode {-Name "TRANS" -Instrument "FGS"}
#
# Removed WALKDOWN, LOS, and MAP in support of OPR 37953
# Frank Tanner - June, 1999
#
#Instrument_Mode {-Name "WALKDOWN" -Instrument "FGS" -Availability "caut-use"}
#Instrument_Mode {-Name "LOS" -Instrument "FGS" -Availability "caut-use"}
#Instrument_Mode {-Name "MAP" -Instrument "FGS" -Availability "caut-use"}

Instrument_Aperture {-Name "1" -Instrument "FGS"}
Instrument_Aperture {-Name "2" -Instrument "FGS"}
Instrument_Aperture {-Name "3" -Instrument "FGS"}

Instrument_Spectral_Element {-Name "F605W" -Instrument "FGS" -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F650W" -Instrument "FGS" -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F583W" -Instrument "FGS" -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "PUPIL" -Instrument "FGS" -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F550W" -Instrument "FGS" -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F5ND" -Instrument "FGS" -Wheel "Wheel1"}

Instrument_Optional_Parameter {-Name "NULL" -Instrument "FGS"
    -Mode {"POS"}
    -Type "string" -String_Values {"YES" "NO"}}
Instrument_Optional_Parameter {-Name "LOCK" -Instrument "FGS"
    -Mode "POS"
    -Type "both" -String_Values {"FINE" "COARSE"} -Min_Val 0 -Max_Val 1 -Availability "eng-only"}
Instrument_Optional_Parameter {-Name "COUNT" -Instrument "FGS"
    -Mode {"POS"}
    -Type "both" -String_Values {"DEF"} -Min_Val 1 -Max_Val 2621400
    -Increment 1}
Instrument_Optional_Parameter {-Name "SCANS" -Instrument "FGS"
    -Mode {"TRANS"}
    -Type "numeric" -Min_Val 1 -Max_Val 200 -Increment 1}
Instrument_Optional_Parameter {-Name "STEP-SIZE" -Instrument "FGS"
    -Mode {"TRANS"}
    -Type "numeric" -Min_Val .03 -Max_Val 10}
Instrument_Optional_Parameter {-Name "ACQ-DIST" -Instrument "FGS"
    -Mode {"POS" "TRANS"}
    -Type "both" -String_Values {"DEF"} -Min_Val 0 -Max_Val 90}
Instrument_Optional_Parameter {-Name "FES-TIME" -Instrument "FGS"
    -Mode {"POS"}
    -Type "string" -String_Values
    {"DEF" "0.025" "0.05" "0.1" "0.2" "0.4" "0.8" "1.6" "3.2"}}

#combinations
Combination {-Type "legal" -Instrument "FGS" -Result {{"mode" "*"}}}
Combination {-Type "legal" -Instrument "FGS" -Result {{"aperture" "*"} {spectral_element "*"}}}

Combination {-Type "illegal" -Instrument "FGS" -Condition {{"aperture" {"2"}}}
    -Result {{spectral_element "F605W"}} -Message
    "Spectral Element F605W cannot be specified with FGS2"}
Combination {-Type "illegal" -Instrument "FGS" -Condition {{"aperture" {"1" "3"}}}
    -Result {{spectral_element "F650W"}} -Message
    "Spectral Element F650W can only be specified with FGS2"}

Combination {-Type "illegal" -Instrument "FGS" -Condition {{"mode" {! "POS"}}}
    -Result {{"calibration_target" "DARK"}} -Message
    "FGS DARK target is only available with POS mode"}

Combination {-Type "illegal" -Instrument "FGS" -Condition {{"mode" "LOS"}} -Result
    {{"exp_time" {!= 47}}}
    -Message "FGS LOS mode must be 47 seconds long."}

#######################################################################################
#
# Instrument S/C
#
#######################################################################################
Print_If_Verbose "S/C forms"
Instrument_Cfg {-Name "S/C" -Instrument "S/C" -Availability "caut-use"}
Instrument_Mode { -Name "DATA" -Instrument "S/C"}
Instrument_Mode { -Name "POINTING" -Instrument "S/C"}
Instrument_Aperture { -Name "V1" -Instrument "S/C"}
Instrument_Aperture { -Name "NONE" -Instrument "S/C"}
#Instrument_Optional_Parameter {-Name "CONTROL" -Instrument "S/C"
#    -Type "string" -String_Values
#    {"DEF" "FGS" "GYRO" "FHST" "1-FGS" "1-FHST" "FGS-FHST"}}

Combination {-Type "legal" -Instrument "S/C" -Result {{"mode" "*"}}}
Combination {-Type "legal" -Instrument "S/C" -Condition {{"mode" "DATA"}}
    -Result {{"aperture" "*"}}}
Combination {-Type "legal" -Instrument "S/C" -Condition {{"mode" "POINTING"}}
    -Result {{"aperture" "V1"}}}

#######################################################################################
#
# Instrument NICMOS
#
#######################################################################################
Print_If_Verbose "NICMOS forms"
Instrument_Cfg {-Name "NIC1" -Instrument "NICMOS"}
Instrument_Cfg {-Name "NIC2" -Instrument "NICMOS"}
Instrument_Cfg {-Name "NIC3" -Instrument "NICMOS"}

Instrument_Mode {-Name "ACQ" -Instrument "NICMOS"}
Instrument_Mode {-Name "ACCUM" -Instrument "NICMOS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "MULTIACCUM" -Instrument "NICMOS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "BRIGHTOBJ" -Instrument "NICMOS" -Availability "caut-use"}
Instrument_Mode {-Name "ALIGN" -Instrument "NICMOS" -Availability "eng-only"}

#apertures
Instrument_Aperture {-Name "NIC1" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC1-FIX" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC1-FIXD" -Instrument "NICMOS" -Availability "caut-use"}
Instrument_Aperture {-Name "NIC2" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC2-FIX" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC2-FIXD" -Instrument "NICMOS" -Availability "caut-use"}
Instrument_Aperture {-Name "NIC2-CORON" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC2-ACQ" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC3" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC3-FIX" -Instrument "NICMOS"}
Instrument_Aperture {-Name "NIC3-FIXD" -Instrument "NICMOS" -Availability "caut-use"}

#spectral_elements
Object_Set {-Name "NIC1-FILTERS" -Type "spectral_element"}
Object_Set {-Name "NIC2-FILTERS" -Type "spectral_element"}
Object_Set {-Name "NIC3-FILTERS" -Type "spectral_element"}
Object_Set {-Name "NIC3-GRISMS" -Type "spectral_element"}
Instrument_Spectral_Element {-Name "BLANK" -Instrument "NICMOS"
    -Object_Sets {"NIC1-FILTERS" "NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "F110W" -Instrument "NICMOS"
    -Min_Wave 0.8 -Max_Wave 1.4 -Object_Sets {"NIC1-FILTERS" "NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "POL240S" -Instrument "NICMOS"
    -Min_Wave 0.81 -Max_Wave 1.29 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "POL120S" -Instrument "NICMOS"
    -Min_Wave 0.81 -Max_Wave 1.29 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "POL0S" -Instrument "NICMOS"
    -Min_Wave 0.81 -Max_Wave 1.29 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F140W" -Instrument "NICMOS"
    -Min_Wave 1.0 -Max_Wave 1.8 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F170M" -Instrument "NICMOS"
    -Min_Wave 1.6 -Max_Wave 1.8 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F187N" -Instrument "NICMOS"
    -Min_Wave 1.875 -Max_Wave 1.875 -Object_Sets {"NIC1-FILTERS" "NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "F190N" -Instrument "NICMOS"
    -Min_Wave 1.9 -Max_Wave 1.9 -Object_Sets {"NIC1-FILTERS" "NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "F165M" -Instrument "NICMOS"
    -Min_Wave 1.55 -Max_Wave 1.75 -Object_Sets {"NIC1-FILTERS" "NIC2-FILTERS"} -Wheel {"Wheel1" "Wheel2"}}
Instrument_Spectral_Element {-Name "F164N" -Instrument "NICMOS"
    -Min_Wave 1.644 -Max_Wave 1.644 -Object_Sets {"NIC1-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel3"}}
Instrument_Spectral_Element {-Name "F166N" -Instrument "NICMOS"
    -Min_Wave 1.66 -Max_Wave 1.66 -Object_Sets {"NIC1-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel3"}}
Instrument_Spectral_Element {-Name "F145M" -Instrument "NICMOS"
    -Min_Wave 1.35 -Max_Wave 1.55 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F160W" -Instrument "NICMOS"
    -Min_Wave 1.4 -Max_Wave 1.8 -Object_Sets {"NIC1-FILTERS" "NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "F113N" -Instrument "NICMOS"
    -Min_Wave 1.13 -Max_Wave 1.13 -Object_Sets {"NIC1-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel3"}}
Instrument_Spectral_Element {-Name "F108N" -Instrument "NICMOS"
    -Min_Wave 1.083 -Max_Wave 1.083 -Object_Sets {"NIC1-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel1" "Wheel3"}}
Instrument_Spectral_Element {-Name "F110M" -Instrument "NICMOS"
    -Min_Wave 1.0 -Max_Wave 1.2 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F090M" -Instrument "NICMOS"
    -Min_Wave 0.8 -Max_Wave 1.0 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F095N" -Instrument "NICMOS"
    -Min_Wave 0.953 -Max_Wave 0.953 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F097N" -Instrument "NICMOS"
    -Min_Wave 0.97 -Max_Wave 0.97 -Object_Sets {"NIC1-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "F204M" -Instrument "NICMOS"
    -Min_Wave 1.99 -Max_Wave 2.09 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "POL240L" -Instrument "NICMOS"
    -Min_Wave 1.9 -Max_Wave 2.1 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "POL120L" -Instrument "NICMOS"
    -Min_Wave 1.9 -Max_Wave 2.1 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "POL0L" -Instrument "NICMOS"
    -Min_Wave 1.9 -Max_Wave 2.1 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "F207M" -Instrument "NICMOS"
    -Min_Wave 2.0 -Max_Wave 2.15 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "F171M" -Instrument "NICMOS"
    -Min_Wave 1.68 -Max_Wave 1.75 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "F180M" -Instrument "NICMOS"
    -Min_Wave 1.765 -Max_Wave 1.835 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "F187W" -Instrument "NICMOS"
    -Min_Wave 1.75 -Max_Wave 2.0 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "F212N" -Instrument "NICMOS"
    -Min_Wave 2.121 -Max_Wave 2.121 -Object_Sets {"NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "F215N" -Instrument "NICMOS"
    -Min_Wave 2.15 -Max_Wave 2.15 -Object_Sets {"NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "F216N" -Instrument "NICMOS"
    -Min_Wave 2.165 -Max_Wave 2.165 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "F222M" -Instrument "NICMOS"
    -Min_Wave 2.15 -Max_Wave 2.30 -Object_Sets {"NIC2-FILTERS" "NIC3-FILTERS"} -Wheel {"Wheel2" "Wheel3"}}
Instrument_Spectral_Element {-Name "F237M" -Instrument "NICMOS"
    -Min_Wave 2.3 -Max_Wave 2.45 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "F205W" -Instrument "NICMOS"
    -Min_Wave 1.75 -Max_Wave 2.35 -Object_Sets {"NIC2-FILTERS"} -Wheel "Wheel2"}
Instrument_Spectral_Element {-Name "G096" -Instrument "NICMOS"
    -Min_Wave 0.8 -Max_Wave 1.2 -Object_Sets {"NIC3-GRISMS"} -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F150W" -Instrument "NICMOS"
    -Min_Wave 1.1 -Max_Wave 1.9 -Object_Sets {"NIC3-FILTERS"} -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "G141" -Instrument "NICMOS"
    -Min_Wave 1.1 -Max_Wave 1.9 -Object_Sets {"NIC3-GRISMS"} -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F196N" -Instrument "NICMOS"
    -Min_Wave 1.962 -Max_Wave 1.962 -Object_Sets {"NIC3-FILTERS"} -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F200N" -Instrument "NICMOS"
    -Min_Wave 2.0 -Max_Wave 2.0 -Object_Sets {"NIC3-FILTERS"} -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F240M" -Instrument "NICMOS"
    -Min_Wave 2.3 -Max_Wave 2.5 -Object_Sets {"NIC3-FILTERS"} -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "G206" -Instrument "NICMOS"
    -Min_Wave 1.4 -Max_Wave 2.5 -Object_Sets {"NIC3-GRISMS"} -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F175W" -Instrument "NICMOS"
    -Min_Wave 1.2 -Max_Wave 2.3 -Object_Sets {"NIC3-FILTERS"} -Wheel "Wheel3"}

#optional_parameters
#Instrument_Optional_Parameter {-Name "NREAD" -Instrument "NICMOS"
#    -Mode {"ACCUM"} -Type "numeric" -Min_Val 1 -Max_Val 25 -Increment 1}
Instrument_Optional_Parameter {-Name "NREAD" -Instrument "NICMOS"
    -Mode {"ACCUM"} -Type "string"
    -String_Values {1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25} -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "SAMP-SEQ" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "string"
    -String_Values {"SCAMRR" "MCAMRR" "STEP1" "STEP2" "STEP8" "STEP16" "STEP32" "STEP64" "STEP128" "STEP256" "SPARS4" "SPARS16" "SPARS32" "SPARS64" "SPARS128" "SPARS256"}
    -Group "SAMP-SEQ-GROUP" -Group_Seq 1 -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "NSAMP" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 1 -Max_Val 25 -Increment 1
    -Group "SAMP-SEQ-GROUP" -Group_Seq 2 -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "SAMP-TIME01" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 1 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME02" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 2 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME03" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 3 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME04" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 4 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME05" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 5 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME06" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 6 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME07" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 7 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME08" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 8 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME09" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 9 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME10" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 10 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME11" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 11 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME12" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 12 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME13" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 13 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME14" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 14 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME15" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 15 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME16" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 16 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME17" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 17 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME18" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 18 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME19" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 19 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME20" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 20 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME21" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 21 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME22" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 22 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME23" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 23 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME24" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 24 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SAMP-TIME25" -Instrument "NICMOS"
    -Mode {"MULTIACCUM"} -Type "numeric" -Min_Val 0.203 -Max_Val 8590.0
    -Group "SAMP-TIME" -Group_Seq 25 -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "READOUT" -Instrument "NICMOS"
    -Mode {"ACCUM" "MULTIACCUM"} -Type "string" -String_Values {"FAST" "SLOW"}
    -Availability "eng-only" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "OFFSET" -Instrument "NICMOS"
    -Mode {"ACCUM" "MULTIACCUM"} -Type "string"
    -String_Values {"SAM" "FOM"} -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "FOMXPOS" -Instrument "NICMOS"
    -Cfg {"NIC1" "NIC2"}
    -Mode {"ACCUM" "MULTIACCUM"} -Type "numeric" -Min_Val -20.0
    -Max_Val 22.0 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "FOMXPOS" -Instrument "NICMOS"
    -Cfg {"NIC3"}
    -Mode {"ACCUM" "MULTIACCUM"} -Type "numeric" -Min_Val -21.0
    -Max_Val 23.0 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "FOMYPOS" -Instrument "NICMOS"
    -Cfg {"NIC1" "NIC2"}
    -Mode {"ACCUM" "MULTIACCUM"} -Type "numeric" -Min_Val -21.0
    -Max_Val 23.0 -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "FOMYPOS" -Instrument "NICMOS"
    -Cfg {"NIC3"}
    -Mode {"ACCUM" "MULTIACCUM"} -Type "numeric" -Min_Val -37.0
    -Max_Val 8.0 -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "LAMP" -Instrument "NICMOS"
    -Mode {"ACCUM" "MULTIACCUM"} -Type "string"
    -String_Values {"NONE" "FLAT1" "FLAT2" "FLAT3"} -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "FOCUS" -Instrument "NICMOS"
    -Cfg "NIC1" -Mode {"ALIGN"} -Type "numeric" -Min_Val -10810 -Max_Val 7538 -Increment 1}
Instrument_Optional_Parameter {-Name "FOCUS" -Instrument "NICMOS"
    -Cfg "NIC2" -Mode {"ALIGN"} -Type "numeric" -Min_Val -9356 -Max_Val 8992 -Increment 1}
Instrument_Optional_Parameter {-Name "FOCUS" -Instrument "NICMOS"
    -Cfg "NIC3" -Mode {"ALIGN"} -Type "numeric" -Min_Val -538 -Max_Val 17810 -Increment 1}
Instrument_Optional_Parameter {-Name "XTILT" -Instrument "NICMOS"
    -Cfg "NIC1" -Mode {"ALIGN"} -Type "numeric" -Min_Val -192 -Max_Val 160 -Increment 1}
Instrument_Optional_Parameter {-Name "XTILT" -Instrument "NICMOS"
    -Cfg "NIC2" -Mode {"ALIGN"} -Type "numeric" -Min_Val -191 -Max_Val 161 -Increment 1}
Instrument_Optional_Parameter {-Name "XTILT" -Instrument "NICMOS"
    -Cfg "NIC3" -Mode {"ALIGN"} -Type "numeric" -Min_Val -166 -Max_Val 186 -Increment 1}
Instrument_Optional_Parameter {-Name "YTILT" -Instrument "NICMOS"
    -Cfg "NIC1" -Mode {"ALIGN"} -Type "numeric" -Min_Val -190 -Max_Val 162 -Increment 1}
Instrument_Optional_Parameter {-Name "YTILT" -Instrument "NICMOS"
    -Cfg "NIC2" -Mode {"ALIGN"} -Type "numeric" -Min_Val -186 -Max_Val 166 -Increment 1}
Instrument_Optional_Parameter {-Name "YTILT" -Instrument "NICMOS"
    -Cfg "NIC3" -Mode {"ALIGN"} -Type "numeric" -Min_Val -181 -Max_Val 171 -Increment 1}

#OPR #34498 & OPR 57777
Instrument_Optional_Parameter {-Name "CAMERA-FOCUS" -Instrument "NICMOS"
    -Mode {"ACCUM" "MULTIACCUM" "ALIGN"} -Type "string"
    -String_Values {"DEF" "1-2" "DEFOCUS"} -Pure_Par_Allowed 1}
#DEFOCUS is avail and eng, but the PP constraint mgr doesn't distinguish
# between the rule above and this one.  It seems to ignore one of the rules,
# so I had to write a reactive check to make sure defocus is only used 
# in available/eng mode
#Instrument_Optional_Parameter {-Name "CAMERA-FOCUS" -Instrument "NICMOS"
#    -Mode {"ACCUM" "MULTIACCUM"} -Type "string"
#    -String_Values {"DEFOCUS"} -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "CAMERA-FOCUS" -Instrument "NICMOS"
    -Mode {"BRIGHTOBJ"} -Type "string"
    -String_Values {"DEF" "1-2" "DEFOCUS"} -Availability "caut-use" -Pure_Par_Allowed 1}

#legal cfg/mode combinations
Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC1" "NIC2" "NIC3"}}}
    -Result {{"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ" "ALIGN"}}}}
Combination {-Type "legal" -Instrument "NICMOS" -Condition {{"cfg" "NIC2"}}
    -Result {{"mode" "ACQ"}}}

#mode/calibration_target combinations
Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"mode" {! "ACCUM" "MULTIACCUM"}}}
    -Result {{"calibration_target" "DARK"}}
    -Message "DARK is only valid for ACCUM, and MULTIACCUM"}

#If target name = DARK, the spectral element must equal BLANK
Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"calibration_target" "DARK"}}
    -Result {{"spectral_element" {! "BLANK"}}}
    -Message "Spectral element must be BLANK with DARK target"}

#If Mode = ALIGN, the target name must equal NONE
Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC1" "NIC2" "NIC3"}} {"mode" "ALIGN"}}
    -Result {{"calibration_target" {! "NONE"}}}
    -Message "ALIGN exposures must have target NONE"}

#legal cfg/spectral_element/aperture combinations
Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "NIC1"} {"mode" {! "ALIGN"}}}
    -Result {{"spectral_element" "NIC1-FILTERS"}}
}
Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "NIC2"} {"mode" {! "ALIGN"}}}
    -Result {{"spectral_element" "NIC2-FILTERS"}}
}
Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "NIC3"} {"mode" {! "ALIGN"}}}
    -Result {{"spectral_element" {"NIC3-FILTERS" "NIC3-GRISMS"}}}
}

Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "NIC1"} {"mode" {! "ALIGN"}}}
    -Result {{"aperture" {"NIC1" "NIC1-FIX" "NIC1-FIXD"}}}
}

Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "NIC2"} {"mode" {! "ACQ" "ALIGN"}}}
    -Result {{"aperture" {"NIC2" "NIC2-FIX" "NIC2-CORON" "NIC2-ACQ" "NIC2-FIXD"}}}
}

Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "NIC2"} {"mode" "ACQ"}}
    -Result {{"aperture" "NIC2-ACQ"}}
}
Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "NIC3"} {"mode" {! "ALIGN"}}}
    -Result {{"aperture" {"NIC3" "NIC3-FIX" "NIC3-FIXD"}}}
}

#exposure times
Combination {-Type "legal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{"exp_time" {"DEF"}}}}
Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{"exp_time" {! "DEF"}}}
    -Message "All MULTIACCUM exposures must have an exposure time of DEF.  The last\
        SAMP-TIME optional parameter or the sequence chosen with SAMP-SEQ and\
        NSAMP will determine the exposure time."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "ACCUM"} {{"optional_parameter" "READOUT"} "FAST"}
                 {{"optional_parameter" "NREAD"} "1"} }
    -Result {{"exp_time" {! 0.57 0.65 0.73 0.80 0.90 1.05 1.26 1.57 2.01 2.86 3.59 4.96 6.88 9.69 12.6 18.0 25.7 40.4 58.2 83.8 110.0 160.0 230.0 361.0 481.0 577.0 961.0 1203.0 1447.0 1861.0 2701.0 3601.0}}}
    -Message "NICMOS ACCUM exps with READOUT=FAST and NREAD=1 are only calibrated for the following exp times 0.57 0.65 0.73 0.80 0.90 1.05 1.26 1.57 2.01 2.86 3.59 4.96 6.88 9.69 12.6 18.0 25.7 40.4 58.2 83.8 110.0 160.0 230.0 361.0 481.0 577.0 961.0 1203.0 1447.0 1861.0 2701.0 3601.0"
}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "ACCUM"} {{"optional_parameter" "READOUT"} "FAST"}
                 {{"optional_parameter" "NREAD"} "10"} }
    -Result {{"exp_time" {! 10.1 12.1 14.9 17.8 23.1 30.9 45.6 63.3 88.9 116.0 165.0 235.0 366.0 486.0 582.0 966.0 1208.0 1452.0 1866.0 2706.0 3606.0}}}
    -Message "NICMOS ACCUM exps with READOUT=FAST and NREAD=10 are only calibrated for the following exp times 10.1 12.1 14.9 17.8 23.1 30.9 45.6 63.3 88.9 116.0 165.0 235.0 366.0 486.0 582.0 966.0 1208.0 1452.0 1866.0 2706.0 3606.0"
}

#illegal optional parameters
#MULTIACCUM SAMP-TIMEs
Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} {{"optional_parameter" "SAMP-SEQ"} "*"}}
    -Result {{{"optional_parameter" {"SAMP-TIME01" "SAMP-TIME02" "SAMP-TIME03" "SAMP-TIME04" "SAMP-TIME05" "SAMP-TIME06" "SAMP-TIME07" "SAMP-TIME08" "SAMP-TIME09" "SAMP-TIME10" "SAMP-TIME11" "SAMP-TIME12" "SAMP-TIME13" "SAMP-TIME14" "SAMP-TIME15" "SAMP-TIME16" "SAMP-TIME17" "SAMP-TIME18" "SAMP-TIME19" "SAMP-TIME20" "SAMP-TIME21" "SAMP-TIME22" "SAMP-TIME23" "SAMP-TIME24" "SAMP-TIME25"}} "*"}}
    -Message "You may not use SAMP-SEQ and SAMP-TIME<n> optional parameters\
        together.  They are mutually exclusive.  Use SAMP-SEQ and\
        NSAMP, OR, fill out the desired number of SAMP-TIME<n> entries."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} {{"optional_parameter" "NSAMP"} "*"}}
    -Result {{{"optional_parameter" {"SAMP-TIME01" "SAMP-TIME02" "SAMP-TIME03" "SAMP-TIME04" "SAMP-TIME05" "SAMP-TIME06" "SAMP-TIME07" "SAMP-TIME08" "SAMP-TIME09" "SAMP-TIME10" "SAMP-TIME11" "SAMP-TIME12" "SAMP-TIME13" "SAMP-TIME14" "SAMP-TIME15" "SAMP-TIME16" "SAMP-TIME17" "SAMP-TIME18" "SAMP-TIME19" "SAMP-TIME20" "SAMP-TIME21" "SAMP-TIME22" "SAMP-TIME23" "SAMP-TIME24" "SAMP-TIME25"}} "*"}}
    -Message "You may not use NSAMP and SAMP-TIME<n> optional parameters\
        together.  They are mutually exclusive.  Use SAMP-SEQ and\
        NSAMP, OR, fill out the desired number of SAMP-TIME<n> entries."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} {{"optional_parameter" "SAMP-SEQ"} "*"}}
    -Result {{{"optional_parameter" "NSAMP"} {! "*"}}}
    -Message "You must supply both SAMP-SEQ and NSAMP together.  Or, supply only\
        SAMP-TIME<n> optional parameters."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} {{"optional_parameter" "SAMP-SEQ"} "*"}}
    -Result {{{"optional_parameter" "READOUT"} "SLOW"}}
    -Message "SAMP-SEQ is incompatible with READOUT=SLOW."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC1" "NIC2" "NIC3"}} {"mode" {"ACCUM"}}}
    -Result {{{"optional_parameter" "NREAD"} {! 1 9}}}
    -Availability "caut-use"
    -Message "NIC NREAD values other than 1 or 9 are available-level only values."}


#OPR 34498 & OPR 57777
Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"*"}} {"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ"}} {{"optional_parameter" "CAMERA-FOCUS"} {"DEF" "1-2"}}}
    -Result {{"aperture" {! "NIC1" "NIC1-FIX" "NIC2" "NIC2-FIX"}}}
    -Message "Optional parameter CAMERA-FOCUS = DEF or 1-2 is legal only with NIC1, NIC1-FIX, NIC2, or NIC2-FIX apertures."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC1"}} {"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ"}} {{"optional_parameter" "CAMERA-FOCUS"} {"DEFOCUS"}}}
    -Result {{"aperture" {! "NIC1-FIXD"}}}
    -Message "When Config = NIC1 and Optional parameter CAMERA-FOCUS = DEFOCUS then the aperture must be NIC1-FIXD."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC1"}} {"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ"}} {"aperture" {"NIC1-FIXD"}}}
    -Result {{{"optional_parameter" "CAMERA-FOCUS"} {! "*"}}}
    -Message "When Config = NIC1 and the aperture is NIC1-FIXD then the Optional parameter CAMERA-FOCUS = DEFOCUS must be supplied "}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC2"}} {"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ"}} {{"optional_parameter" "CAMERA-FOCUS"} {"DEFOCUS"}}}
    -Result {{"aperture" {! "NIC2-FIXD"}}}
    -Message "When Config = NIC2 and Optional parameter CAMERA-FOCUS = DEFOCUS then the aperture must be NIC2-FIXD."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC2"}} {"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ"}} {"aperture" {"NIC2-FIXD"}}}
    -Result {{{"optional_parameter" "CAMERA-FOCUS"} {! "*"}}}
    -Message "When Config = NIC2 and the aperture is NIC2-FIXD then the Optional parameter CAMERA-FOCUS = DEFOCUS must be supplied "}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC3"}} {"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ"}} {{"optional_parameter" "CAMERA-FOCUS"} {"DEFOCUS"}}}
    -Result {{"aperture" {! "NIC3-FIXD"}}}
    -Message "When Config = NIC3 and Optional parameter CAMERA-FOCUS = DEFOCUS then the aperture must be NIC3-FIXD."}

Combination {-Type "illegal" -Instrument "NICMOS"
    -Condition {{"cfg" {"NIC3"}} {"mode" {"ACCUM" "MULTIACCUM" "BRIGHTOBJ"}} {"aperture" {"NIC3-FIXD"}}}
    -Result {{{"optional_parameter" "CAMERA-FOCUS"} {! "*"}}}
    -Message "When Config = NIC3 and the aperture is NIC3-FIXD then the Optional parameter CAMERA-FOCUS = DEFOCUS must be supplied "}

#######################################################################################
#
# Instrument STIS
#
#######################################################################################
Print_If_Verbose "STIS forms"
Instrument_Cfg {-Name "STIS/FUV-MAMA" -Instrument "STIS"}
Instrument_Cfg {-Name "STIS/NUV-MAMA" -Instrument "STIS"}
Instrument_Cfg {-Name "STIS/CCD" -Instrument "STIS"}
Instrument_Cfg {-Name "STIS" -Instrument "STIS" -Availability "eng-only"}
Instrument_Mode { -Name "ACCUM" -Instrument "STIS" -Pure_Par_Allowed 1}
Instrument_Mode { -Name "ACQ" -Instrument "STIS"}
Instrument_Mode { -Name "ACQ/PEAK" -Instrument "STIS"}
Instrument_Mode { -Name "ALIGN" -Instrument "STIS" -Availability "eng-only"}
Instrument_Mode { -Name "ANNEAL" -Instrument "STIS" -Availability "eng-only"}
Instrument_Mode { -Name "MSMOFF" -Instrument "STIS" -Availability "eng-only"}
Instrument_Mode { -Name "TIME-TAG" -Instrument "STIS"}

#aperture sets
Object_Set {-Name "ACQ_CCD_SUPPORT" -Type "aperture"}
Object_Set {-Name "PEAK_CCD_SUPPORT" -Type "aperture"}
Object_Set {-Name "PEAK_CCD_AVAIL" -Type "aperture"}
Object_Set {-Name "PEAK_CCD_RES" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUM_CCD_SUPPORT" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUM_CCD_AVAIL" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUM_CCD_RES" -Type "aperture"}
Object_Set {-Name "G_ACCUM_CCD_SUPPORT" -Type "aperture"}
Object_Set {-Name "G_ACCUM_CCD_AVAIL" -Type "aperture"}
Object_Set {-Name "G_ACCUM_CCD_RES" -Type "aperture"}
Object_Set {-Name "GF_ACCUM_CCD_SUPPORT" -Type "aperture"}
Object_Set {-Name "GF_ACCUM_CCD_AVAIL" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUMTIME_MAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUMTIME_FUVMAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUMTIME_FUVMAMA_RES" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUMTIME_NUVMAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUMTIME_MAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "MIRROR_ACCUMTIME_MAMA_RES" -Type "aperture"}
Object_Set {-Name "G_ACCUMTIME_MAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "G_ACCUMTIME_MAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "G_ACCUMTIME_MAMA_RES" -Type "aperture"}
Object_Set {-Name "G_ACCUMTIME_FUVMAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "GE_ACCUMTIME_FUVMAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "GE_ACCUMTIME_NUVMAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "GEPRISM_ACCUMTIME_NUVMAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "GEPRISM_ACCUMTIME_MAMA_RES" -Type "aperture"}
Object_Set {-Name "E_ACCUMTIME_MAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "E_ACCUMTIME_MAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "E_H_ACCUMTIME_MAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "E_H_ACCUMTIME_MAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "E_H_ACCUMTIME_NUVMAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "E_H_ACCUMTIME_FUVMAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "E_M_ACCUMTIME_MAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "E_M_ACCUMTIME_MAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "PRISM_ACCUMTIME_NUVMAMA_SUPPORT" -Type "aperture"}
Object_Set {-Name "PRISM_ACCUMTIME_NUVMAMA_AVAIL" -Type "aperture"}
Object_Set {-Name "PRISM_ACCUMTIME_NUVMAMA_RES" -Type "aperture"}
Object_Set {-Name "G_NOFLAT_CCD_SUPPORT" -Type "aperture"}
Object_Set {-Name "G_FLAT_CCD_SUPPORT" -Type "aperture"}
Object_Set {-Name "G_WAVE_STIS_APERTURE_GROUP" -Type "aperture"}
Object_Set {-Name "G_WAVE_STIS_APERTURE_GROUP_G230L" -Type "aperture"}
Object_Set {-Name "G_WAVE_STIS_APERTURE_GROUP_PRISM" -Type "aperture"}
Object_Set {-Name "G_WAVE_STIS_APERTURE_GROUP_E140H" -Type "aperture"}
Object_Set {-Name "G_WAVE_STIS_APERTURE_GROUP_E140M" -Type "aperture"}
Object_Set {-Name "G_WAVE_STIS_APERTURE_GROUP_E230H" -Type "aperture"}
Object_Set {-Name "G_WAVE_STIS_APERTURE_GROUP_E230M" -Type "aperture"}

Object_Set {-Name "X_ACCUMTIME_MAMA_RES" -Type "aperture"}
Object_Set {-Name "CORONOGRAPHIC" -Type "aperture"}


Instrument_Aperture {-Name "DEF" -Instrument "STIS" -Availability "caut-use"}

#Defined apertures
#This can be generated by the code in PP/bin/sort-stis-aps.tcl, using the
#stis-aps input file in there.  All tags have to be defined properly.
Instrument_Aperture {-Name "0.05X29" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES X_ACCUMTIME_MAMA_RES}}
Instrument_Aperture {-Name "0.05X31NDA" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES X_ACCUMTIME_MAMA_RES}}
Instrument_Aperture {-Name "0.05X31NDB" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES X_ACCUMTIME_MAMA_RES}}
Instrument_Aperture {-Name "0.09X29" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES X_ACCUMTIME_MAMA_RES}}
Instrument_Aperture {-Name "0.1X0.03" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_AVAIL G_WAVE_STIS_APERTURE_GROUP_E140H G_WAVE_STIS_APERTURE_GROUP_E140M G_WAVE_STIS_APERTURE_GROUP_E230H G_WAVE_STIS_APERTURE_GROUP_E230M}}
Instrument_Aperture {-Name "0.1X0.06" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "0.1X0.09" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_H_ACCUMTIME_NUVMAMA_SUPPORT E_H_ACCUMTIME_FUVMAMA_AVAIL E_M_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_WAVE_STIS_APERTURE_GROUP_E230H}}
Instrument_Aperture {-Name "0.1X0.2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_H_ACCUMTIME_NUVMAMA_SUPPORT E_H_ACCUMTIME_FUVMAMA_AVAIL E_M_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_WAVE_STIS_APERTURE_GROUP_E230H}}
Instrument_Aperture {-Name "0.2X0.05ND" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "0.2X0.06" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_H_ACCUMTIME_MAMA_AVAIL E_M_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_AVAIL G_FLAT_CCD_SUPPORT G_WAVE_STIS_APERTURE_GROUP_E140M G_WAVE_STIS_APERTURE_GROUP_E230M}}
Instrument_Aperture {-Name "0.2X0.06FPA" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.06FPB" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.06FPC" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.06FPD" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.06FPE" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.09" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_H_ACCUMTIME_MAMA_SUPPORT E_M_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_WAVE_STIS_APERTURE_GROUP_E140H G_WAVE_STIS_APERTURE_GROUP_E230H}}
Instrument_Aperture {-Name "0.2X0.2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_AVAIL G_WAVE_STIS_APERTURE_GROUP_E140H G_WAVE_STIS_APERTURE_GROUP_E140M G_WAVE_STIS_APERTURE_GROUP_E230M G_WAVE_STIS_APERTURE_GROUP_E230H}}
Instrument_Aperture {-Name "0.2X0.2FPA" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.2FPB" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.2FPC" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.2FPD" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.2FPE" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_RES E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_RES}}
Instrument_Aperture {-Name "0.2X0.5" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "0.2X29" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES X_ACCUMTIME_MAMA_RES}}
Instrument_Aperture {-Name "0.3X0.05ND" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "0.3X0.06" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "0.3X0.09" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_FLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "0.3X0.2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "0.5X0.5" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "1X0.06" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "1X0.2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "25MAMA" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "25MAMAD1" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "2X2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_AVAIL G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "31X0.05NDA" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "31X0.05NDB" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "31X0.05NDC" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT G_WAVE_STIS_APERTURE_GROUP_G230L}}
Instrument_Aperture {-Name "36X0.05N45" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "36X0.05P45" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "36X0.6N45" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "36X0.6P45" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "50CCD" -Instrument "STIS"
    -Object_Sets {ACQ_CCD_SUPPORT MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "50CORON" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES }}
Instrument_Aperture {-Name "52X0.05" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_FLAT_CCD_SUPPORT G_WAVE_STIS_APERTURE_GROUP G_WAVE_STIS_APERTURE_GROUP_G230L G_WAVE_STIS_APERTURE_GROUP_PRISM}}
Instrument_Aperture {-Name "52X0.05D1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.05E1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.05F1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.05F1-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL}}
Instrument_Aperture {-Name "52X0.05E2" -Instrument "STIS"
    -Object_Sets {G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.05F2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.05F2-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL}}
Instrument_Aperture {-Name "52X0.1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_FLAT_CCD_SUPPORT G_WAVE_STIS_APERTURE_GROUP G_WAVE_STIS_APERTURE_GROUP_G230L}}
Instrument_Aperture {-Name "52X0.1B0.5" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1B0.5-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1B1.0" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1B1.0-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1B3.0" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1B3.0-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1D1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1E1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1E2" -Instrument "STIS"
    -Object_Sets {G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1F1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1F1-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL}}
Instrument_Aperture {-Name "52X0.1F2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.1F2-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL}}
Instrument_Aperture {-Name "52X0.2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_FLAT_CCD_SUPPORT G_WAVE_STIS_APERTURE_GROUP G_WAVE_STIS_APERTURE_GROUP_G230L G_WAVE_STIS_APERTURE_GROUP_PRISM}}
Instrument_Aperture {-Name "52X0.2D1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.2E1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.2E2" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_AVAIL GF_ACCUM_CCD_SUPPORT GF_ACCUM_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.2F1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_FLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.2F1-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.2F2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT G_WAVE_STIS_APERTURE_GROUP G_WAVE_STIS_APERTURE_GROUP_G230L}}
Instrument_Aperture {-Name "52X0.2F2-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL}}
Instrument_Aperture {-Name "52X0.5" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_FLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.5D1" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.5E1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.5E2" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_AVAIL GF_ACCUM_CCD_SUPPORT GF_ACCUM_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.5F1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "52X0.5F1-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES}}
Instrument_Aperture {-Name "52X0.5F2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X0.5F2-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES}}
Instrument_Aperture {-Name "52X2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_FLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X2D1" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X2E1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X2E2" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_AVAIL GF_ACCUM_CCD_SUPPORT GF_ACCUM_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X2F1" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X2F1-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X2F2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "52X2F2-R" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "6X0.06" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "6X0.2" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_AVAIL MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_AVAIL G_WAVE_STIS_APERTURE_GROUP_E140H G_WAVE_STIS_APERTURE_GROUP_E140M G_WAVE_STIS_APERTURE_GROUP_E230H G_WAVE_STIS_APERTURE_GROUP_E230M}}
Instrument_Aperture {-Name "6X0.5" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_RES G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "6X6" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_AVAIL G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_AVAIL G_ACCUMTIME_MAMA_AVAIL E_ACCUMTIME_MAMA_AVAIL PRISM_ACCUMTIME_NUVMAMA_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "BAR10" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "F25CIII" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_NUVMAMA_SUPPORT GEPRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "F25CN182" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_NUVMAMA_SUPPORT GEPRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "F25CN270" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_NUVMAMA_SUPPORT GEPRISM_ACCUMTIME_NUVMAMA_AVAIL}}
Instrument_Aperture {-Name "F25LYA" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_FUVMAMA_SUPPORT GE_ACCUMTIME_FUVMAMA_AVAIL}}
Instrument_Aperture {-Name "F25MGII" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_NUVMAMA_SUPPORT GE_ACCUMTIME_NUVMAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT}}
Instrument_Aperture {-Name "F25ND3" -Instrument "STIS"
    -Object_Sets {ACQ_CCD_SUPPORT MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25ND5" -Instrument "STIS"
    -Object_Sets {ACQ_CCD_SUPPORT MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25NDQ1" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25NDQ2" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25NDQ3" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25NDQ4" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25QTZ" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25QTZD1" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25SRF2" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_RES G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_SUPPORT G_ACCUMTIME_MAMA_SUPPORT E_ACCUMTIME_MAMA_SUPPORT PRISM_ACCUMTIME_NUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F25SRF2D1" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUMTIME_FUVMAMA_RES G_ACCUMTIME_FUVMAMA_SUPPORT G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F28X50LP" -Instrument "STIS"
    -Object_Sets {ACQ_CCD_SUPPORT MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F28X50OII" -Instrument "STIS"
    -Object_Sets {ACQ_CCD_SUPPORT MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "F28X50OIII" -Instrument "STIS"
    -Object_Sets {ACQ_CCD_SUPPORT MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_AVAIL G_NOFLAT_CCD_SUPPORT}}
Instrument_Aperture {-Name "WEDGEA0.6" -Instrument "STIS"
    -Object_Sets {MIRROR_ACCUM_CCD_SUPPORT CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEA1.0" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEA1.8" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEA2.0" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEA2.5" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEA2.8" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEB1.0" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEB1.8" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEB2.0" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEB2.5" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
Instrument_Aperture {-Name "WEDGEB2.8" -Instrument "STIS"
    -Object_Sets {PEAK_CCD_RES MIRROR_ACCUM_CCD_SUPPORT G_ACCUM_CCD_RES MIRROR_ACCUMTIME_MAMA_RES GEPRISM_ACCUMTIME_MAMA_RES CORONOGRAPHIC}}
#End of Defined Apertures.  Cut above to replace from sorted code generator.

#spectral_elements
Object_Set {-Name "STIS-FUV-FILTERS" -Type "spectral_element"}
Object_Set {-Name "STIS-NUV-FILTERS" -Type "spectral_element"}
Object_Set {-Name "STIS-CCD-FILTERS" -Type "spectral_element"}
Object_Set {-Name "STIS-CCD-FLAT-FILTERS" -Type "spectral_element"}

Instrument_Spectral_Element {-Name "DEF" -Instrument "STIS" -Availability "caut-use"
    -Wheel "Wheel1"}

Instrument_Spectral_Element {-Name "G140L" -Instrument "STIS" -Wave_List {1425}
    -Object_Sets {"STIS-FUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G140M" -Instrument "STIS"
    -Wave_List {1173 1218 1222 1272 1321 1371 1387 1400 1420 1470 1518 1540 1550 1567 1616 1640 1665 1714}
    -Object_Sets {"STIS-FUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "E140M" -Instrument "STIS" -Wave_List {1425}
    -Object_Sets {"STIS-FUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "E140H" -Instrument "STIS"
    -Wave_List {1234 1271 1307 1343 1380 1416 1453 1489 1526 1562 1598}
    -Object_Sets {"STIS-FUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "X140M" -Instrument "STIS" -Availability "eng-only"
    -Wave_List {1425}
    -Object_Sets {"STIS-FUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "X140H" -Instrument "STIS" -Availability "eng-only"
    -Wave_List {1232 1269 1305 1341 1378 1414 1451 1487 1523 1560 1587}
    -Object_Sets {"STIS-FUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G230L" -Instrument "STIS"
    -Wave_List {2376}
    -Object_Sets {"STIS-NUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G230M" -Instrument "STIS"
    -Wave_List {1687 1769 1851 1884 1933 2014 2095 2176 2257 2338 2419 2499 2579 2600 2659 2739 2800 2818 2828 2898 2977 3055}
    -Object_Sets {"STIS-NUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "E230M" -Instrument "STIS"
    -Wave_List {1978 2124 2269 2415 2561 2707}
    -Object_Sets {"STIS-NUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "E230H" -Instrument "STIS"
    -Wave_List {1763 1813 1863 1913 1963 2013 2063 2113 2163 2213 2263 2313 2363 2413 2463 2513 2563 2613 2663 2713 2762 2812 2862 2912 2962 3012}
    -Object_Sets {"STIS-NUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "X230M" -Instrument "STIS" -Availability "eng-only"
    -Wave_List {1975 2703}
    -Object_Sets {"STIS-NUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "X230H" -Instrument "STIS" -Availability "eng-only"
    -Wave_List {1760 2010 2261 2511 2760 3010}
    -Object_Sets {"STIS-NUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "PRISM" -Instrument "STIS" -Wave_List {1200 2125}
    -Object_Sets {"STIS-NUV-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G230LB" -Instrument "STIS" -Wave_List {2375}
    -Object_Sets {"STIS-CCD-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G230MB" -Instrument "STIS"
    -Wave_List {1713 1854 1995 2135 2276 2416 2557 2697 2794 2836 2976 3115}
    -Object_Sets {"STIS-CCD-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G430L" -Instrument "STIS" -Wave_List {4300}
    -Object_Sets {"STIS-CCD-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G430M" -Instrument "STIS"
    -Wave_List {3165 3305 3423 3680 3843 3936 4194 4451 4706 4781 4961 5093 5216 5471}
    -Object_Sets {"STIS-CCD-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G750L" -Instrument "STIS" -Wave_List {7751 8975}
    -Object_Sets {"STIS-CCD-FLAT-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G750M" -Instrument "STIS"
    -Wave_List {5734 6094 6252 6581 6768 7283 7795 8311 8561 8825 9286 9336 9806 9851 10363}
    -Object_Sets {"STIS-CCD-FLAT-FILTERS"} -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "MIRROR" -Instrument "STIS"
    -Object_Sets {"STIS-FUV-FILTERS" "STIS-NUV-FILTERS" "STIS-CCD-FILTERS"}
    -Wheel "Wheel1"}

#optional_parameters

# Make all lamps caut-use and restrict with combinations
Instrument_Optional_Parameter {-Name "LAMP" -Instrument "STIS" -Mode "ACCUM"
    -Type "string" -String_Values {"HITM1" "HITM2" "LINE" "DEUTERIUM" "KRYPTON" "TUNGSTEN"}
    -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "LAMP" -Instrument "STIS" -Mode "TIME-TAG"
    -Type "string" -String_Values {"HITM1" "HITM2" "LINE" "DEUTERIUM" "KRYPTON"}
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "BUFFER-TIME" -Instrument "STIS" -Mode "TIME-TAG"
    -Type "numeric" -Min_Val 40 -Max_Val 20000000 -Increment 1}

Instrument_Optional_Parameter {-Name "CR-SPLIT" -Instrument "STIS"
    -Cfg "STIS/CCD" -Mode "ACCUM" -Type "string"
    -String_Values {"NO" "2" "3" "4" "5" "6" "7" "8"}}
Instrument_Optional_Parameter {-Name "GAIN" -Instrument "STIS"
    -Cfg "STIS/CCD" -Mode "ACCUM" -Type "string" -String_Values {"1" "2" "4" "8"} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "GAIN" -Instrument "STIS"
    -Cfg "STIS/CCD" -Mode {"ACQ" "ACQ/PEAK"}
    -Type "string" -String_Values {"1" "2" "4" "8"} -Availability "caut-use"}
#
# X-axis BINAXIS2
#
Instrument_Optional_Parameter {-Name "BINAXIS2" -Instrument "STIS" -Mode "ACCUM"
    -Cfg "STIS/CCD" -Type "string" -String_Values {1 2 4} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "BINAXIS2" -Instrument "STIS" -Mode "ACCUM"
    -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}
    -Type "string" -String_Values {"DEF" "NO" "YES"}}
#
# Y-axis BINAXIS1
#
Instrument_Optional_Parameter {-Name "BINAXIS1" -Instrument "STIS" -Mode "ACCUM"
    -Cfg "STIS/CCD" -Type "string" -String_Values {1 2 4} -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "BINAXIS1" -Instrument "STIS" -Mode "ACCUM"
    -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}
    -Type "string" -String_Values {"DEF" "NO" "YES"}}
#
# X-axis SIZEAXIS2
#
Instrument_Optional_Parameter {-Name "SIZEAXIS2" -Instrument "STIS" -Cfg "STIS/CCD" -Mode {"ACCUM"}
    -Type "both" -String_Values {"FULL"} -Min_Val 30 -Max_Val 1022 -Increment 1
    -Group SEARCH -Group_Seq 5 -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "SIZEAXIS2" -Instrument "STIS" -Cfg "STIS/CCD" -Mode {"ACQ/PEAK"}
    -Type "both" -String_Values {"FULL"} -Min_Val 16 -Max_Val 1022 -Increment 1
    -Group SEARCH -Group_Seq 5}

Instrument_Optional_Parameter {-Name "SIZEAXIS2" -Instrument "STIS" -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"} -Mode {"ACCUM" "ACQ/PEAK" "TIME-TAG"}
    -Type "string" -String_Values {"FULL" 16 32 64 128 256 512}
    -Group SEARCH -Group_Seq 5}
#
# Y-axis SIZEAXIS1
#
Instrument_Optional_Parameter {-Name "SIZEAXIS1" -Instrument "STIS" -Mode {"ACCUM"}
    -Cfg "STIS/CCD"
    -Type "both" -String_Values {"FULL"} -Min_Val 30 -Max_Val 1060 -Increment 1
    -Availability "caut-use"
    -Group SEARCH -Group_Seq 5 -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "SIZEAXIS1" -Instrument "STIS" -Mode {"ACQ/PEAK"}
    -Cfg "STIS/CCD"
    -Type "both" -String_Values {"FULL"} -Min_Val 16 -Max_Val 1060 -Increment 1
    -Availability "caut-use"
    -Group SEARCH -Group_Seq 5}

Instrument_Optional_Parameter {-Name "SIZEAXIS1" -Instrument "STIS" -Mode {"ACCUM" "TIME-TAG"}
    -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}
    -Type "string" -String_Values {"FULL" 16 32 64 128 256 512}
    -Group SEARCH -Group_Seq 5}

Instrument_Optional_Parameter {-Name "SIZEAXIS1" -Instrument "STIS" -Mode {"ACQ/PEAK"}
    -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}
    -Type "string" -String_Values {"FULL" 16 32 64 128 256 512}
    -Availability "caut-use"
    -Group SEARCH -Group_Seq 5}
#
# X-axis - CENTERAXIS2
#
Instrument_Optional_Parameter {-Name "CENTERAXIS2" -Instrument "STIS" -Mode {"ACCUM"} -Cfg "STIS/CCD"
    -Type "both" -String_Values {"TARGET"} -Min_Val 17 -Max_Val 1009 -Increment 1
    -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "CENTERAXIS2" -Instrument "STIS" -Mode {"ACQ/PEAK"} -Cfg "STIS/CCD"
    -Type "both" -String_Values {"TARGET"} -Min_Val 10 -Max_Val 1016 -Increment 1
    -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "CENTERAXIS2" -Instrument "STIS" -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"} -Mode {"ACCUM" "TIME-TAG"}
    -Type "both" -String_Values {"TARGET"} -Min_Val 9 -Max_Val 1017 -Increment 1}

Instrument_Optional_Parameter {-Name "CENTERAXIS2" -Instrument "STIS" -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"} -Mode {"ACQ/PEAK"}
    -Type "both" -String_Values {"TARGET"} -Min_Val 9 -Max_Val 1017 -Increment 1
    -Availability "caut-use"}
#
# Y-axis - CENTERAXIS1
#
Instrument_Optional_Parameter {-Name "CENTERAXIS1" -Instrument "STIS" -Mode {"ACCUM"}
    -Cfg "STIS/CCD" -Type "both" -String_Values {"TARGET"}
    -Min_Val 17 -Max_Val 1047 -Increment 1 -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "CENTERAXIS1" -Instrument "STIS" -Mode {"ACQ/PEAK"}
    -Cfg "STIS/CCD" -Type "both" -String_Values {"TARGET"}
    -Min_Val 10 -Max_Val 1054 -Increment 1 -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "CENTERAXIS1" -Instrument "STIS"
    -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"} -Mode {"ACCUM" "ACQ/PEAK" "TIME-TAG"}
    -Type "both" -String_Values {"TARGET"} -Min_Val 9 -Max_Val 1017 -Increment 1
    -Availability "caut-use"}
#
# Do not allow subarrays with STIS MAMA detectors (OPR_48215)
#
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/FUV-MAMA"} {"mode" "*"}}
    -Result {{{"optional_parameter" {"SIZEAXIS1" "SIZEAXIS2" "CENTERAXIS1" "CENTERAXIS2"}} {"*"}}}
    -Message "STIS Optional Parameter(s) SIZEAXIS1, SIZEAXIS2, CENTERAXIS1 and CENTERAXIS2 are invalid for Config FUV-MAMA"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/NUV-MAMA"} {"mode" "*"}}
    -Result {{{"optional_parameter" {"SIZEAXIS1" "SIZEAXIS2" "CENTERAXIS1" "CENTERAXIS2"}} {"*"}}}
    -Message "STIS Optional Parameter(s) SIZEAXIS1, SIZEAXIS2, CENTERAXIS1 and CENTERAXIS2 are invalid for Config NUV-MAMA"}

Instrument_Optional_Parameter {-Name "WAVECAL" -Instrument "STIS"
    -Mode {"ACCUM" "TIME-TAG"} -Type "string"
    -String_Values {"NO"} -Availability "caut-use" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "PREFLUSH" -Instrument "STIS"
    -Cfg "STIS/CCD" -Mode "ACCUM" -Type "string"
    -String_Values {"YES" "NO"} -Availability "caut-use" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "ACQTYPE" -Instrument "STIS" -Mode "ACQ" -Type "string"
    -String_Values {"POINT" "DIFFUSE"}}
Instrument_Optional_Parameter {-Name "DIFFUSE-CENTER" -Instrument "STIS" -Mode "ACQ" -Type "string"
    -String_Values {"FLUX-CENTROID" "GEOMETRIC-CENTER"}}
Instrument_Optional_Parameter {-Name "CHECKBOX" -Instrument "STIS" -Mode "ACQ" -Type "numeric"
    -Min_Val 3 -Max_Val 105 -Increment 2}

Instrument_Optional_Parameter {-Name "SEARCH" -Instrument "STIS" -Mode "ACQ/PEAK" -Type "string"
    -String_Values {"DEF" "SPIRAL" "LINEARAXIS1" "LINEARAXIS2"} -Availability "caut-use"
    -Group SEARCH -Group_Seq 1
}
Instrument_Optional_Parameter {-Name "NUM-POS" -Instrument "STIS" -Mode "ACQ/PEAK"
    -Type "both" -String_Values {"DEF"} -Min_Val 3 -Max_Val 49 -Increment 2
    -Availability "caut-use" -Group SEARCH -Group_Seq 2
}
Instrument_Optional_Parameter {-Name "STEP-SIZE" -Instrument "STIS" -Mode "ACQ/PEAK"
    -Type "both" -String_Values {"DEF"} -Min_Val 1 -Max_Val 1000 -Increment 1
    -Availability "caut-use" -Group SEARCH -Group_Seq 3
}
Instrument_Optional_Parameter {-Name "CENTROID" -Instrument "STIS" -Mode "ACQ/PEAK" -Type "string"
    -String_Values {"YES" "NO"} -Availability "caut-use"
    -Group SEARCH -Group_Seq 4
}

Instrument_Optional_Parameter {-Name "FOCUS" -Instrument "STIS" -Mode "ALIGN" -Type "numeric"
    -Min_Val -4791 -Max_Val 4791 -Availability "eng-only"}
Instrument_Optional_Parameter {-Name "XTILT" -Instrument "STIS" -Mode "ALIGN" -Type "numeric"
    -Min_Val -115 -Max_Val 115 -Availability "eng-only"}
Instrument_Optional_Parameter {-Name "YTILT" -Instrument "STIS" -Mode "ALIGN" -Type "numeric"
    -Min_Val -115 -Max_Val 115 -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "SLIT-STEP" -Instrument "STIS"
    -Mode "ACCUM" -Cfg "STIS/CCD" -Type "numeric"
    -Min_Val -31000 -Max_Val 31000 -Increment 1
    -Availability "eng-only" -Pure_Par_Allowed 1}
Instrument_Optional_Parameter {-Name "SLIT-STEP" -Instrument "STIS"
    -Mode "ACCUM" -Cfg {"STIS/FUV-MAMA" "STIS/NUV-MAMA"} -Type "numeric"
    -Min_Val -10000 -Max_Val 10000 -Increment 1
    -Availability "eng-only" -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "AMP" -Instrument "STIS"
    -Mode "ACCUM" -Cfg "STIS/CCD" -Type "string"
    -String_Values {"A" "B" "C" "D"}
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "POS" -Instrument "STIS"
    -Mode "ACCUM" -Cfg {"STIS/CCD" "STIS/FUV-MAMA"} -Type "string"
    -String_Values {"1.1-0" "1.1-1" "3.2-0" "3.2-1" "3.2-2" "3.2-3" "3.2-4" "3.6-0" "3.6-1" "3.6-2" "3.6-3" "3.6-4" "3.6-5" "3.6-6" "3.6-7" "3.6-8"}
    -Availability "eng-only"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACCUM"} {"spectral_element" "G430M"}}
    -Result {{{"optional_parameter" "POS"} {! "3.2-0" "3.2-1" "3.2-2" "3.2-3" "3.2-4"}}}
    -Message "STIS/CCD Optional Parameter POS is invalid for Mode ACCUM, Spectral Element G430M"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACCUM"} {"spectral_element" "MIRROR"}}
    -Result {{{"optional_parameter" "POS"} {! "3.6-0" "3.6-1" "3.6-2" "3.6-3" "3.6-4" "3.6-5" "3.6-6" "3.6-7" "3.6-8"}}}
    -Message "STIS/CCD Optional Parameter POS is invalid for Mode ACCUM, Spectral Element MIRROR"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/FUV-MAMA"} {"mode" "ACCUM"} {"spectral_element" "G140L"}}
    -Result {{{"optional_parameter" "POS"} {! "1.1-0" "1.1-1"}}}
    -Message "STIS/FUV-MAMA Optional Parameter POS is invalid for Mode ACCUM, Spectral Element G140L"}

# STIS MSMOFF optional parameters
Instrument_Optional_Parameter {-Name "SETOFFSET" -Instrument "STIS"
    -Mode {"MSMOFF"} -Group "STIS-MSMOFF" -Group_Seq 1 -Type "string"
    -String_Values {"ZERO" "RESTORE" "0100" "0200" "0300" "0400" "0500" "0600" "0700" "0800" "0900" "1000" "1100" "1200"}}
Instrument_Optional_Parameter {-Name "GRATING1" -Instrument "STIS"
    -Mode {"MSMOFF"} -Group "STIS-MSMOFF" -Group_Seq 2 -Type "string"
    -String_Values {"ALL" "G140L" "G140M" "G230L" "G230M"}}
Instrument_Optional_Parameter {-Name "GRATING2" -Instrument "STIS"
    -Mode {"MSMOFF"} -Group "STIS-MSMOFF" -Group_Seq 3 -Type "string"
    -String_Values {"G140L" "G140M" "G230L" "G230M"}}
Instrument_Optional_Parameter {-Name "GRATING3" -Instrument "STIS"
    -Mode {"MSMOFF"} -Group "STIS-MSMOFF" -Group_Seq 4 -Type "string"
    -String_Values {"G140L" "G140M" "G230L" "G230M"}}
Instrument_Optional_Parameter {-Name "WAVELENGTH" -Instrument "STIS"
    -Mode {"MSMOFF"} -Group "STIS-MSMOFF" -Group_Seq 5 -Type "numeric"
    -Min_Val 1000 -Max_Val 10000 -Increment 1}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACQ/PEAK"} {{"optional_parameter" "SIZEAXIS2"} {< 30}}}
    -Result {{"spectral_element" {! "MIRROR"}}}
    -Message "Must use MIRROR spectral element to perform a subarray smaller than 30."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACQ/PEAK"} {{"optional_parameter" "SIZEAXIS1"} {< 30}}}
    -Result {{"spectral_element" {! "MIRROR"}}}
    -Message "Must use MIRROR spectral element to perform a subarray smaller than 30."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACQ/PEAK"} {{"optional_parameter" "CENTERAXIS2"} {< 17}}}
    -Result {{"spectral_element" {! "MIRROR"}}}
    -Message "Must use MIRROR spectral element to perform a subarray smaller than 30."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACQ/PEAK"} {{"optional_parameter" "CENTERAXIS2"} {> 1009}}}
    -Result {{"spectral_element" {! "MIRROR"}}}
    -Message "Must use MIRROR spectral element to perform a subarray smaller than 30."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACQ/PEAK"} {{"optional_parameter" "CENTERAXIS1"} {< 17}}}
    -Result {{"spectral_element" {! "MIRROR"}}}
    -Message "Must use MIRROR spectral element to perform a subarray smaller than 30."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACQ/PEAK"} {{"optional_parameter" "CENTERAXIS1"} {> 1047}}}
    -Result {{"spectral_element" {! "MIRROR"}}}
    -Message "Must use MIRROR spectral element to perform a subarray smaller than 30."}

#combinations

# Make lamps not tungsten illegal unless eng-only

Combination {-Type "illegal" -Instrument "STIS"
   -Result {{{"optional_parameter" "LAMP"} {! "TUNGSTEN"}}}
   -Availability "eng-only"
   -Message "Lamps except TUNGSTEN not allowed in non-engineering proposals."}

# Make none calibration target illegal if no lamp is specified
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"calibration_target" {"NONE"}}}
    -Result {{{"optional_parameter" "LAMP"} {! "*"}}}
    -Availability "eng-only"
    -Message "Calibration Target 'NONE' only allowed in engineering proposals unless LAMP is TUNGSTEN"}

# Make none calibration target illegal if lamp is not tungsten if not eng-only
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"calibration_target" {"NONE"}}}
    -Result {{{"optional_parameter" "LAMP"} {! "TUNGSTEN"}}}
    -Availability "eng-only"
    -Message "Calibration Target 'NONE' only allowed in engineering proposals unless LAMP is TUNGSTEN"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {! "STIS"}}}
    -Result {{"spectral_element" {! "*"}}}
    -Message "Spectral Element must be specified.  Legal apertures are dependent on\
        the Spectral Element and all apertures are illegal until a Spectral\
        Element is selected."}

#legal cfg/mode combinations
Combination {-Type "legal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}}
    -Result {{"mode" {"TIME-TAG" "ACCUM"}}}}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}}
    -Result {{"mode" {"ACQ/PEAK"}}}
    -Availability "eng-only"}
Combination {-Type "legal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"}}
    -Result {{"mode" {"ACQ" "ACQ/PEAK" "ACCUM"}}}}
Combination {-Type "legal" -Instrument "STIS"
    -Condition {{"cfg" "STIS"}}
    -Result {{"mode" {"ALIGN" "ANNEAL" "MSMOFF"}}}}

#illegal cfg/calibration_target combinations
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}}
    -Result {{"calibration_target" "EARTH-CALIB"}}
    -Message "EARTH-CALIB is not allowed with STIS/FUV-MAMA or STIS/NUV-MAMA configuration."
}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {! "STIS/CCD"}}}
    -Result {{"calibration_target" {"BIAS" "CCDFLAT"}}}
    -Message "Calibration Target BIAS and CCDFLAT can only be used with Config STIS/CCD."
}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"mode" "ACCUM"}}
    -Result {{"calibration_target" {"DARK" "BIAS"}}}
    -Message "DARK and BIAS are engineering only"
    -Availability "eng-only"}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"mode" {! "ACCUM"}}}
    -Result {{"calibration_target" {"WAVE" "CCDFLAT"}}}
    -Message "WAVE and CCDFLAT targets are only allowed in ACCUM mode."}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"calibration_target" "WAVE"}}
    -Result {{"spectral_element" {"MIRROR" "X140H" "X140M" "X230H" "X230M"}}}
    -Message "You can not use MIRROR, X140H, X140M, X230H, or X230M spectral elements\
        when using the WAVE calibration target."}

#legal calibration target combinations
Combination {-Type "legal" -Instrument "STIS"
    -Condition {{"calibration_target" {"DARK" "BIAS"}}}
    -Result {{"aperture" {"DEF"}}}}
Combination {-Type "legal" -Instrument "STIS"
    -Condition {{"calibration_target" {"DARK" "BIAS"}}}
    -Result {{"spectral_element" {"DEF"}}}}
Combination {-Type "legal" -Instrument "STIS"
    -Condition {{"calibration_target" {"WAVE" "CCDFLAT"}}}
    -Result {{"exp_time" {"DEF"}}}}
Combination {-Type "legal" -Instrument "STIS"
    -Condition {{"mode" {"MSMOFF"}}}
    -Result {{"exp_time" "DEF"}}}

Combination {-Type "illegal" -Instrument "STIS" -Condition
    {{"calibration_target" "BIAS"}}
    -Result {{"exp_time" {!= 0}}}
    -Message "STIS BIAS must be given an exposure time of zero"}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"mode" {"MSMOFF"}}}
    -Result {{"exp_time" {! "DEF"}}}
    -Message "Exposure time must be DEF for MSMOFF exposures"}

#-----------------------------------------------
#Aperture/Spectral Element Combinations
#SUPPORTED spectral_element/aperture combinations
Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" "ACQ"}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "ACQ_CCD_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" "ACQ/PEAK"}
         {"spectral_element" {"*"}}}
    -Result {{"aperture" "PEAK_CCD_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" "ACCUM"}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUM_CCD_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" "ACCUM"}
         {"spectral_element" {"G230LB" "G230MB" "G430L" "G430M" "G750L" "G750M"}}}
    -Result {{"aperture" "G_ACCUM_CCD_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" "ACCUM"}
         {"spectral_element" {"G750L" "G750M"}}}
    -Result {{"aperture" "GF_ACCUM_CCD_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUMTIME_MAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA"}} {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUMTIME_FUVMAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/NUV-MAMA"}} {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUMTIME_NUVMAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G140L" "G140M" "G230L" "G230M"}}}
    -Result {{"aperture" "G_ACCUMTIME_MAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G140L" "G140M"}}}
    -Result {{"aperture" "G_ACCUMTIME_FUVMAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E140M" "E140H" "E230M" "E230H"}}}
    -Result {{"aperture" "E_ACCUMTIME_MAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G230L" "G230M" "E230H" "E230M"}}}
    -Result {{"aperture" "GE_ACCUMTIME_NUVMAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E140H" "E230H"}}}
    -Result {{"aperture" "E_H_ACCUMTIME_MAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E230H"}}}
    -Result {{"aperture" "E_H_ACCUMTIME_NUVMAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E140M" "E230M"}}}
    -Result {{"aperture" "E_M_ACCUMTIME_MAMA_SUPPORT"}}}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/NUV-MAMA"}} {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"PRISM"}}}
    -Result {{"aperture" "PRISM_ACCUMTIME_NUVMAMA_SUPPORT"}}}


#AVAILABLE se/aperture combos
Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" {"ACQ/PEAK"}}
         {"spectral_element" {"*"}}}
    -Result {{"aperture" "PEAK_CCD_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" {"ACCUM"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUM_CCD_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" {"ACCUM"}}
         {"spectral_element" {"G230LB" "G230MB" "G430L" "G430M" "G750L" "G750M"}}}
    -Result {{"aperture" "G_ACCUM_CCD_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" {"ACCUM"}}
         {"spectral_element" {"G230LB" "G230MB" "G430L" "G430M"}}}
    -Result {{"aperture" "GF_ACCUM_CCD_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUMTIME_MAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G140L" "G140M" "G230L" "G230M"}}}
    -Result {{"aperture" "G_ACCUMTIME_MAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G140L" "G140M" "E140H" "E140M"}}}
    -Result {{"aperture" "GE_ACCUMTIME_FUVMAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G230L" "G230M" "E230H" "E230M" "PRISM"}}}
    -Result {{"aperture" "GEPRISM_ACCUMTIME_NUVMAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E140H" "E140M" "E230H" "E230M"}}}
    -Result {{"aperture" "E_ACCUMTIME_MAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E140H" "E230H"}}}
    -Result {{"aperture" "E_H_ACCUMTIME_MAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E140M" "E230M"}}}
    -Result {{"aperture" "E_M_ACCUMTIME_MAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"E140H"}}}
    -Result {{"aperture" "E_H_ACCUMTIME_FUVMAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"PRISM"}}}
    -Result {{"aperture" "PRISM_ACCUMTIME_NUVMAMA_AVAIL"}}
    -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "STIS" -trackAvailability 1
    -Condition {{"spectral_element" {"G750M"}}}
    -Result {{"wavelength" "10363"}}
    -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "STIS" -trackAvailability 1
    -Condition {{"spectral_element" {"G750L"}}}
    -Result {{"wavelength" "8975"}}
    -Availability "caut-use"}

#RESTRICTED se/aperture combos
Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" {"ACQ/PEAK"}}
         {"spectral_element" {"*"}}}
    -Result {{"aperture" "PEAK_CCD_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" {"ACCUM"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUM_CCD_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/CCD"}} {"mode" {"ACCUM"}}
         {"spectral_element" {"G230LB" "G230MB" "G430L" "G430M" "G750L" "G750M"}}}
    -Result {{"aperture" "G_ACCUM_CCD_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G140L" "G140M" "G230L" "G230M"}}}
    -Result {{"aperture" "G_ACCUMTIME_MAMA_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUMTIME_FUVMAMA_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"MIRROR"}}}
    -Result {{"aperture" "MIRROR_ACCUMTIME_MAMA_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"PRISM"}}}
    -Result {{"aperture" "PRISM_ACCUMTIME_NUVMAMA_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
         {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"G140L" "G140M" "E140H" "E140M" "G230L" "G230M" "E230H" "E230M" "PRISM"}}}
    -Result {{"aperture" "GEPRISM_ACCUMTIME_MAMA_RES"}}
    -Availability "eng-only"}

Combination {-Type "legal" -Instrument "STIS" -trackAvailability 1
     -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"mode" {"ACCUM" "TIME-TAG"}}
         {"spectral_element" {"X140H" "X140M" "X230H" "X230M"}}}
    -Result {{"aperture" "X_ACCUMTIME_MAMA_RES"}}
    -Availability "eng-only"}


#CCDFLAT aperture restrictions/extensions
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/CCD"}} {"calibration_target" {"CCDFLAT"}}}
    -Result {{"aperture" "G_NOFLAT_CCD_SUPPORT"}}
    -Message "Only a subset of the apertures available to the G spectral elements are allowed for CCDFLATs."}

Combination {-Type "illegal" -Instrument "STIS"
        -Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"WAVE"}}
            {"spectral_element" {"G230LB" "G230MB" "G430L" "G430M" "G750L" "G750M" "G140L" "G140M" "G230M"}}}
    -Result {{"aperture" {! "G_WAVE_STIS_APERTURE_GROUP"}}}
    -Message "This spectral type is not valid for WAVE targets."}

Combination {-Type "illegal" -Instrument "STIS"
        -Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"WAVE"}}
            {"spectral_element" {"G230L"}}}
    -Result {{"aperture" {! "G_WAVE_STIS_APERTURE_GROUP_G230L"}}}
    -Message "This spectral type is not valid for WAVE targets."}
    
Combination {-Type "illegal" -Instrument "STIS"
        -Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"WAVE"}}
            {"spectral_element" {"PRISM"}}}
    -Result {{"aperture" {! "G_WAVE_STIS_APERTURE_GROUP_PRISM"}}}
    -Message "This spectral type is not valid for WAVE targets."}
    
Combination {-Type "illegal" -Instrument "STIS"
        -Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"WAVE"}}
            {"spectral_element" {"E140H"}}}
    -Result {{"aperture" {! "G_WAVE_STIS_APERTURE_GROUP_E140H"}}}
    -Message "This spectral type is not valid for WAVE targets."}
    
Combination {-Type "illegal" -Instrument "STIS"
        -Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"WAVE"}}
            {"spectral_element" {"E140M"}}}
    -Result {{"aperture" {! "G_WAVE_STIS_APERTURE_GROUP_E140M"}}}
    -Message "This spectral type is not valid for WAVE targets."}
    
Combination {-Type "illegal" -Instrument "STIS"
        -Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"WAVE"}}
            {"spectral_element" {"E230H"}}}
    -Result {{"aperture" {! "G_WAVE_STIS_APERTURE_GROUP_E230H"}}}
    -Message "This spectral type is not valid for WAVE targets."}
    
Combination {-Type "illegal" -Instrument "STIS"
        -Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"WAVE"}}
            {"spectral_element" {"E230M"}}}
    -Result {{"aperture" {! "G_WAVE_STIS_APERTURE_GROUP_E230M"}}}
    -Message "This spectral type is not valid for WAVE targets."}
    


Combination {-Type "legal" -Instrument "STIS"
     -Condition {{"cfg" {"STIS/CCD"}} {"calibration_target" {"CCDFLAT"}}}
     -Result {{"aperture" "G_FLAT_CCD_SUPPORT"}}}
#----------------------------------------------
# End of aperture/se combinations
#----------------------------------------------

#legal cfg/spectral_element combinations, and mode/spectral_element combinations
Combination {-Type "legal" -Instrument "STIS" -Condition {{"cfg" "STIS/FUV-MAMA"} {"mode" "*"}}
    -Result {{"spectral_element" "STIS-FUV-FILTERS"}}}
Combination {-Type "legal" -Instrument "STIS" -Condition {{"cfg" "STIS/NUV-MAMA"} {"mode" "*"}}
    -Result {{"spectral_element" "STIS-NUV-FILTERS"}}}

Combination {-Type "legal" -Instrument "STIS" -Condition {{"cfg" "STIS/CCD"} {"mode" {"ACCUM" "ACQ/PEAK"}}}
    -Result {{"spectral_element" {"STIS-CCD-FILTERS" "STIS-CCD-FLAT-FILTERS"}}}}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" {"ACCUM"}} {"calibration_target" "CCDFLAT"}}
    -Result {{"spectral_element" {! "STIS-CCD-FLAT-FILTERS"}}}
    -Message "CCDFLAT exposures can only use the G750L and G750M filters."}

Combination {-Type "legal" -Instrument "STIS" -Condition {{"cfg" "STIS/CCD"} {"mode" "ACQ"}}
    -Result {{"spectral_element" "MIRROR"}}}

#illegal cfg/optional_parameter combinations
Combination {-Type "illegal" -Instrument "STIS" -Condition {{"cfg" "STIS/CCD"}}
    -Result {{{"optional_parameter" "LAMP"} {"KRYPTON"}}}
    -Message "KRYPTON is an illegal value for LAMP with STIS/CCD"}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {! "STIS/CCD"}}}
    -Result {{{"optional_parameter" "LAMP"} {"TUNGSTEN"}}}
    -Message "TUNGSTEN is an illegal value for LAMP with STIS/FUV-MAMA and STIS/NUV-MAMA"}

#illegal optional parameter combinations

# MAMA subarrays
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}}
    {"mode" {"ACCUM" "TIME-TAG"}} {{"optional_parameter" "SIZEAXIS1"} {"*"}}}
    -Result {{"spectral_element" {! "MIRROR" "PRISM"}}}
    -Availability "caut-use"
    -Message "SIZEAXIS1 is an available-level optional parameter in MAMA ACCUM or\
        TIME-TAG mode, unless you use the MIRROR or PRISM spectral elements."}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"mode" {"ACCUM" "TIME-TAG"}}
    {{"optional_parameter" "CENTERAXIS2"} {"*"}}}
    -Result {{"spectral_element" {! "E140M" "E140H" "E230M" "E230H"}}}
    -Availability "caut-use"
    -Message "CENTERAXIS2 is an available-level optional parameter in\
        MAMA ACCUM or TIME-TAGE modes, unless you use the echelle spectral\
        elements (E140M, E140H, E230M, E230H)."}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" "LAMP"} {"*"}}}
    -Result {{"calibration_target" { ! "NONE"}}} -Message "No target is allowed with LAMPs"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" "SLIT-STEP"} {"*"}}}
    -Result {{"calibration_target" { ! "NONE"}}} -Message "No target is allowed with SLIT-STEP"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" "SLIT-STEP"} {"*"}}}
    -Result {{{"optional_parameter" "LAMP"} {"HITM1" "HITM2" "LINE"}}}
    -Message "SLIT-STEP is only allowed when the LAMP optional parameter is\
        either KRYPTON, DEUTERIUM, or TUNGSTEN."}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" "SLIT-STEP"} {"*"}}}
    -Result {{{"optional_parameter" "LAMP"} {! "*"}}}
    -Message "SLIT-STEP is only allowed if the LAMP optional parameter is also\
        used, where LAMP must be either KRYPTON, DEUTERIUM, or TUNGSTEN."}


Combination {-Type "illegal" -Instrument "STIS"
-Condition {{"cfg" {"STIS/CCD" "STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"mode" {"ACCUM"}} {"calibration_target" "NONE"}}
    -Result {{{"optional_parameter" "LAMP"} {! "*"}}}
    -Message "When Configuration is STIS/CCD, STIS/FUV-MAMA, STIS/NUV-MAMA, Mode is ACCUM, and Target is NONE \
        you must supply the LAMP optional Parameter."}

# STIS Engineering Wavecal Constraints for LAMP parameters
# This is implemented both as a reactive and a proactive check
# It is in ExposureSpecification too, in order to create a 
# Health and Safety Error.
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"E140H"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "0.2X0.09" "0.2X0.2" "6X0.2" "0.1X0.03"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."}    

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"E140M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "0.2X0.06" "0.2X0.2" "6X0.2" "0.1X0.03"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"E230H"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "0.1X0.09" "0.1X0.2" "6X0.2" "0.1X0.03" "1X0.06" "0.2X0.09" "0.2X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"E230H"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
                {{"wavelength"}  {! "2713"}}
               }
    -Result {{{"aperture"} {"1X0.06"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
   -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"E230H"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
                {{"wavelength"} {! "2363"}}
               }
    -Result {{{"aperture"} {"0.2X0.09" "0.2X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"E230M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "0.2X0.06" "0.2X0.2" "6X0.2" "0.1X0.03" "0.1X0.09" "0.1X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"E230M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
                {{"wavelength"}  {! "2269"}}
               }
    -Result {{{"aperture"} {"0.1X0.09" "0.1X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."}    
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140L"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"wavelength"} {! "1425"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140L"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "52X0.05" "52X0.1" "52X0.2" "52X0.2F1" "0.2X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."}     
   
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140L"}}
                {{"optional_parameter" "LAMP"} {"HITM1"}}
               }
    -Result {{{"wavelength"} {! "1425"}}}
    -Message "LAMP HITM1 is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140L"}}
                {{"optional_parameter" "LAMP"} {"HITM1"}}
               }
    -Result {{{"aperture"} {! "52X0.5" "52X2"}}}
    -Message "LAMP HITM1 is not a valid parameter for this configuration."}
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "52X0.05" "52X0.1" "52X0.2" "52X0.5" "52X2" "52X0.2F1" "0.2X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
                {{"wavelength"}  {! "1420"}}
               }
    -Result {{{"aperture"} {"0.2X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."}   
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140M"}}
                {{"optional_parameter" "LAMP"} {"HITM1" "HITM2"}}
               }
    -Result {{{"wavelength"}  {! "1173"}}}
    -Message "LAMP HITM1/2 is not a valid parameter for this configuration."}   
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G140M"}}
                {{"optional_parameter" "LAMP"} {"HITM1" "HITM2"}}
               }
    -Result {{{"aperture"} {! "52X0.05" "52X0.1" "52X0.2"}}}
    -Message "LAMP HITM1/2 is not a valid parameter for this configuration."}   
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230L"}}
                {{"optional_parameter" "LAMP"} {"HITM1"}}
               }
    -Result {{{"aperture"} {! "52X0.1" "52X0.2" "52X0.2F1"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230L"}}
                {{"optional_parameter" "LAMP"} {"HITM2"}}
               }
    -Result {{{"aperture"} {! "52X0.5"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
   
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230L"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "52X0.05" "0.2X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "52X0.05" "52X0.1" "52X0.2" "52X0.5" "52X0.2F1" "0.2X0.2" "52X2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
                {{"wavelength"}  {! "2338"}}
               }
    -Result {{{"aperture"} {"0.2X0.2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
                {{"wavelength"}  {! "1687" "1769" "1851" "1884" "2014" "2095" "2176" "2257" "2338" "2419" "2499" "2579" "2600"}}
               }
    -Result {{{"aperture"} {"52X2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
        
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230M"}}
                {{"optional_parameter" "LAMP"} {"HITM1"}}
               }
    -Result {{{"aperture"} {! "52X2"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."} 
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"G230M"}}
                {{"optional_parameter" "LAMP"} {"HITM1"}}
               }
    -Result {{{"wavelength"} {! "1933" "2659" "2739" "2800" "2818" "2828" "2898" "2977" "3055"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."}
    
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"PRISM"}}
               }
    -Result {{{"optional_parameter" "LAMP"} {"LINE" "HITM2"}}}
    -Message "LAMP must be HITM1 when used with PRISM."}   

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"PRISM"}}
                {{"optional_parameter" "LAMP"} {"HITM1"}}
               }
    -Result {{{"aperture"} {! "52X0.05"}}}
    -Message "LAMP HITM1 is not a valid parameter for this configuration."}   

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {"X140H" "X140M" "X230H" "X230M"}}
                {{"optional_parameter" "LAMP"} {"LINE"}}
               }
    -Result {{{"aperture"} {! "0.05X29"}}}
    -Message "LAMP LINE is not a valid parameter for this configuration."}
    
# HITM1 is only valid for G140L, G140M, G230L, G230M, and PRISM
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {! "G140L" "G140M" "G230L" "G230M" "PRISM"}}                
               }
    -Result {{{"optional_parameter" "LAMP"} {"HITM1"}}}
    -Message "LAMP HITM1 is not a valid parameter for this configuration."}
    
# HITM2 is only valid for G140M, G230L
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} 
                {"spectral_element" {! "G140M" "G230L"}}                
               }
    -Result {{{"optional_parameter" "LAMP"} {"HITM2"}}}
    -Message "LAMP HITM2 is not a valid parameter for this configuration."}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"mode" {"TIME-TAG"}}}
    -Result {{{"optional_parameter" "BUFFER-TIME"} {! "*"}}}
    -Message "STIS TIME-TAG mode must have a BUFFER-TIME optional parameter"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS"}} {"mode" {"ANNEAL" "ALIGN" "MSMOFF"}}}
    -Result {{"calibration_target" {! "NONE"}}}
    -Message "ALIGN, ANNEAL and MSMOFF exposures must have target NONE"}


Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" {"BINAXIS1" "BINAXIS2"} {"*"}}}}
    -Result {{{"optional_parameter" {"SIZEAXIS1" "SIZEAXIS2" "CENTERAXIS1" "CENTERAXIS2"}}}}
    -Message "Binning and subarray optional parameters are mutually exclusive"}
#
# STIS/CCD target-CCDFLAT valid OPs = BINAXIS1 and BINAXIS2 (OPR_48260)
#
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"calibration_target" "CCDFLAT"}}
    -Result {{{"optional_parameter" {"WAVECAL" "GAIN" "CENTERAXIS2" "CR-SPLIT" "SIZEAXIS1" "SIZEAXIS2" "CENTERAXIS1" "PREFLUSH" "AMP" "POS"}} {"*"}}}
    -Message "No optional parameters other than BINAXIS1 and BINAXIS2 are allowed with CCDFLAT targets."}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" {"ACQTYPE"}} {! "DIFFUSE"}}}
    -Result {{{"optional_parameter" {"DIFFUSE-CENTER" "CHECKBOX"}}}}
    -Message "DIFFUSE-CENTER and CHECKBOX optional parameters are only legal with ACQTYPE DIFFUSE"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" {"ACQTYPE"}} {"DIFFUSE"}}}
    -Result {{{"optional_parameter" {"CHECKBOX"}} {! "*"}}}
    -Message "CHECKBOX must be specified with ACQTYPE DIFFUSE"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" {"ACQTYPE"}} {"DIFFUSE"}}}
    -Result {{{"optional_parameter" {"DIFFUSE-CENTER"}} {! "*"}}}
    -Message "DIFFUSE-CENTER must be specified with ACQTYPE DIFFUSE"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" {"DIFFUSE-CENTER"}} {"*"}}}
    -Result {{{"optional_parameter" {"ACQTYPE"}} {! "*"}}}
    -Message "DIFFUSE-CENTER can only be specified if ACQTYPE DIFFUSE"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{{"optional_parameter" {"CHECKBOX"}} {"*"}}}
    -Result {{{"optional_parameter" {"ACQTYPE"}} {! "*"}}}
    -Message "CHECKBOX can only be specified if ACQTYPE DIFFUSE"}

Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"mode" "ACCUM"}}
    -Result {{{"optional_parameter" "GAIN"} {"2" "8"}}}
    -Availability "caut-use"
    -Message "GAIN optional parameter only has SUPPORTED values of 1 and 4."}
#
# Added in support of OPR 38499
# Frank Tanner - May, 1999
#
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"mode" "ACQ"}}
    -Result {{"exp_time" {>= 300}}}
    -Availability "caut-use"
    -Message "STIS ACQ exposures must be less than 5 minutes in a GO proposal."}
#
# Added in support of OPR 39357
# Frank Tanner - June, 1999
#
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"calibration_target" {"DARK" "BIAS"}}}
    -Result {{"spectral_element" {! "DEF"}}}
    -Message "STIS/CCD with target DARK or BIAS must specify spectral element DEF."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" "STIS/CCD"} {"calibration_target" {"DARK" "BIAS"}}}
    -Result {{"aperture" {! "DEF"}}}
    -Message "STIS/CCD with target DARK or BIAS must specify aperture DEF."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"DARK"}}}
    -Result {{"aperture" {! "DEF"}}}
    -Message "STIS/FUV-MAMA and STIS/NUV-MAMA with target DARK must specify aperture DEF."}
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/FUV-MAMA" "STIS/NUV-MAMA"}} {"calibration_target" {"DARK"}}}
    -Result {{"spectral_element" {! "DEF"}}}
    -Message "STIS/FUV-MAMA and STIS/NUV-MAMA with target DARK must specify spectral element DEF."}
Combination {-Type "illegal" -Instrument "STIS"
   -Condition {{"cfg" {"STIS"}}}
   -Result {{"calibration_target" {! "NONE"}}}
   -Message "Only target NONE is allowed with config STIS."}   

# No EARTH-CALIB with STIS-CCD (PR 71145)
#
Combination {-Type "illegal" -Instrument "STIS"
    -Condition {{"cfg" {"STIS/CCD"}}}
    -Result {{"calibration_target" {"EARTH-CALIB"}}}
    -Message "EARTH-CALIB is not allowed with the STIS/CCD configuration."}

   
#######################################################################################
#
# Instrument WFC3
#
#######################################################################################
Print_If_Verbose "WFC3 forms"
Instrument_Cfg {-Name "WFC3/UVIS" -Instrument "WFC3" -Pure_Par_Allowed 1}
Instrument_Cfg {-Name "WFC3/IR"   -Instrument "WFC3" -Pure_Par_Allowed 1}
Instrument_Cfg {-Name "WFC3"      -Instrument "WFC3" -Availability "eng-only"}

#
# WFC3 Instrument Modes
#
Instrument_Mode {-Name "ACCUM"      -Instrument "WFC3" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "MULTIACCUM" -Instrument "WFC3" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "ALIGN"      -Instrument "WFC3" -Availability "eng-only"}
Instrument_Mode {-Name "ANNEAL"     -Instrument "WFC3" -Availability "eng-only"}

#
# WFC3 Apertures
#
Object_Set {-Name "WFC3-UVIS-ACCUM-APERTURES" -Type "aperture"}
Object_Set {-Name "WFC3-UVIS-QUAD-APERTURES" -Type "aperture"}

Object_Set {-Name "WFC3-UVIS-SUB-APERTURES" -Type "aperture"}
Object_Set {-Name "WFC3-IR-SUB-APERTURES" -Type "aperture"}
# all GRISM apertures except 1024 which is the full array
Object_Set {-Name "WFC3-IR-GRISM-SUBS" -Type "aperture"}
# This object set contains all IR-SUB* apertures, but excludes IR-SUB*-FIX apertures.
Object_Set {-Name "WFC3-IR-SUB-NOT-FIX-APERTURES" -Type "aperture"}
Object_Set {-Name "WFC3-IR-MULTIACCUM-APERTURES" -Type "aperture"}
Object_Set {-Name "WFC3-IR-GRISM-APERTURES" -Type "aperture"}

#
# WFC3/UVIS Apertures
#
Instrument_Aperture {-Name "UVIS" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS-CENTER" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS1" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS1-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS2" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS2-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS-QUAD" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-APERTURES"}}
Instrument_Aperture {-Name "UVIS-QUAD-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-APERTURES"}}
Instrument_Aperture {-Name "G280-REF" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}
Instrument_Aperture {-Name "UVIS-QUAD-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-APERTURES"}}
Instrument_Aperture {-Name "UVIS1-2K4-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} -Availability "caut-use"}
Instrument_Aperture {-Name "UVIS1-M512-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} -Availability "caut-use"}
Instrument_Aperture {-Name "UVIS1-C512A-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} -Availability "caut-use"}
Instrument_Aperture {-Name "UVIS1-C512B-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} -Availability "caut-use"}
Instrument_Aperture {-Name "UVIS2-2K4-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} -Availability "eng-only"}
Instrument_Aperture {-Name "UVIS2-M512-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} -Availability "eng-only"}
Instrument_Aperture {-Name "UVIS2-C512C-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} }
Instrument_Aperture {-Name "UVIS2-C512D-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"} -Availability "eng-only"}
Instrument_Aperture {-Name "UVIS2-M512C-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"}}
Instrument_Aperture {-Name "UVIS2-M1K1C-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"}}
Instrument_Aperture {-Name "UVIS2-C1K1C-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"}}
Instrument_Aperture {-Name "UVIS1-2K2A-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"}}
Instrument_Aperture {-Name "UVIS1-2K2B-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"}}
Instrument_Aperture {-Name "UVIS2-2K2C-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"}}
Instrument_Aperture {-Name "UVIS2-2K2D-SUB" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-SUB-APERTURES"}}
Instrument_Aperture {-Name "UVIS-IR-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-APERTURES"}}


#
# WFC3/IR Apertures
#
Instrument_Aperture {-Name "IR" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES"}}
Instrument_Aperture {-Name "IR-UVIS" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES"}}
Instrument_Aperture {-Name "IR-UVIS-CENTER" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES"}}
Instrument_Aperture {-Name "IR-UVIS-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES"}}
Instrument_Aperture {-Name "IR-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES"}}
Instrument_Aperture {-Name "G102-REF" -Instrument "WFC3" -Availability "caut-use"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES"}}
Instrument_Aperture {-Name "G141-REF" -Instrument "WFC3" -Availability "caut-use"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES"}}

Instrument_Aperture {-Name "IRSUB64" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES" "WFC3-IR-SUB-NOT-FIX-APERTURES"}}
Instrument_Aperture {-Name "IRSUB64-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES"}}
Instrument_Aperture {-Name "IRSUB128" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES" "WFC3-IR-SUB-NOT-FIX-APERTURES"}}
Instrument_Aperture {-Name "IRSUB128-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES"}}
Instrument_Aperture {-Name "IRSUB256" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES" "WFC3-IR-SUB-NOT-FIX-APERTURES"}}
Instrument_Aperture {-Name "IRSUB256-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES"}}
Instrument_Aperture {-Name "IRSUB512" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES" "WFC3-IR-SUB-NOT-FIX-APERTURES"}}
Instrument_Aperture {-Name "IRSUB512-FIX" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-SUB-APERTURES"}}

Instrument_Aperture {-Name "GRISM1024" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-GRISM-APERTURES"}} 
Instrument_Aperture {-Name "GRISM512" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-GRISM-APERTURES" "WFC3-IR-GRISM-SUBS"}}
Instrument_Aperture {-Name "GRISM256" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-GRISM-APERTURES" "WFC3-IR-GRISM-SUBS"}}
Instrument_Aperture {-Name "GRISM128" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-GRISM-APERTURES" "WFC3-IR-GRISM-SUBS"}}
Instrument_Aperture {-Name "GRISM64" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-APERTURES" "WFC3-IR-GRISM-APERTURES" "WFC3-IR-GRISM-SUBS"}}

#
# WFC3 Spectral Elements
#
Object_Set {-Name "WFC3-UVIS-ACCUM-FILTERS" -Type "spectral_element"}
Object_Set {-Name "WFC3-UVIS-QUAD-FILTERS" -Type "spectral_element"}
Object_Set {-Name "WFC3-UVIS-G-FILTERS" -Type "spectral_element"}
Object_Set {-Name "WFC3-IR-MULTIACCUM-FILTERS" -Type "spectral_element"}
Object_Set {-Name "WFC3-IR-G-FILTERS" -Type "spectral_element"}

#
# WFC3/UVIS Spectral Elements
#
Instrument_Spectral_Element {-Name "F218W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F200LP" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F225W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F275W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F280N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F300X" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F336W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F343N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F350LP" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F373N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F390M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F390W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F395N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F410M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F438W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F467M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F469N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F475W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F475X" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F487N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F502N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F547M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F555W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F600LP" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F606W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F621M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F625W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F631N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F645N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F656N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F657N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F658N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F665N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F673N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F680N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F689M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F763M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F775W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F814W" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F845M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F850LP" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F953N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ232N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ243N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ378N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ387N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ422M" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ436N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ437N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ492N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ508N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ575N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ619N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ634N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ672N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ674N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ727N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ750N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ889N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ906N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ924N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "FQ937N" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-QUAD-FILTERS"}}
Instrument_Spectral_Element {-Name "G280" -Instrument "WFC3"
    -Object_Sets {"WFC3-UVIS-ACCUM-FILTERS" "WFC3-UVIS-G-FILTERS"}}
Instrument_Spectral_Element {-Name "DEF" -Instrument "WFC3"}

#
# WFC3/IR Spectral Elements
#
Instrument_Spectral_Element {-Name "F098M" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F105W" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F125W" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F126N" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F127M" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F128N" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F130N" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F132N" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F139M" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F140W" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F110W" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F153M" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F160W" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F164N" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "F167N" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"}}
Instrument_Spectral_Element {-Name "G102" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS" "WFC3-IR-G-FILTERS"}}
Instrument_Spectral_Element {-Name "G141" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS" "WFC3-IR-G-FILTERS"}}
Instrument_Spectral_Element {-Name "BLANK" -Instrument "WFC3"
    -Object_Sets {"WFC3-IR-MULTIACCUM-FILTERS"} -Availability "eng-only"}


#
# WFC3/UVIS Optional Parameters
#

Instrument_Optional_Parameter {-Name "BIN" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"NONE" "2" "3"}
    -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "CR-SPLIT" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"NO" "2" "3" "4" "5" "6" "7" "8"}
    -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "GAIN" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"1.0" "1.5" "2.0" "4.0"} -Pure_Par_Allowed 1 -Availability "eng-only"}

#---- POST-FLASH parameters

Instrument_Optional_Parameter {-Name "FLASH" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "numeric"
    -Pure_Par_Allowed 1
    -Min_Val 1 -Max_Val 25 -Increment 1
}
Instrument_Optional_Parameter {-Name "FLASHEXP" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "numeric"
    -Min_Val 0.1 -Max_Val 409.5
    # Pure par enabled for testing of leakage (by engineering)
    -Pure_Par_Allowed 1
    -Availability "eng-only"}
Instrument_Optional_Parameter {-Name "FLASHCUR" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    # Pure par enabled for testing of leakage (by engineering)
    -Pure_Par_Allowed 1
    -String_Values {"LOW" "MEDIUM" "HIGH"}
    -Availability "eng-only"}

# FLASH cannot be specified with FLASHCUR or FLASHEXP
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASH"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHEXP"} {"*"}}}
    -Message "FLASH cannot be specified with FLASHEXP."}
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASH"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHCUR"} {"*"}}}
    -Message "FLASH cannot be specified with FLASHCUR."}

# FLASH, FLASHEXP and FLASHCUR are not allowed with BIAS (PR 72486)
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}
	{"calibration_target" {"BIAS"}}}
    -Result {{{"optional_parameter" {"FLASH" "FLASHEXP" "FLASHCUR"} "*"}}}
    -Message "FLASH, FLASHEXP and FLASHCUR cannot be specified with the BIAS internal target."}


# FLASHCUR and FLASHEXP require one another
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASHCUR"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHEXP"} {! "*"}}}
    -Message "If FLASHCUR is specified, FLASHEXP must also be specified."}
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASHEXP"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHCUR"} {! "*"}}}
    -Message "If FLASHEXP is specified, FLASHCUR must also be specified."}
#----(end of post-flash)

Instrument_Optional_Parameter {-Name "AMP" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"A" "B" "C" "D" "AC" "AD" "BC" "BD" "ABCD"} -Pure_Par_Allowed 1 -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "CURRENT" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"LOW" "MEDIUM" "HIGH"} -Pure_Par_Allowed 1 -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "SIZEAXIS2" -Instrument "WFC3"
    -Pure_Par_Allowed 1
    -Cfg {"WFC3/UVIS"} -Mode {"ACCUM"} -Type "both" -String_Values {"FULL"}
    -Min_Val 16 -Max_Val 2050 -Increment 1 -Pure_Par_Allowed 1
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "SIZEAXIS1" -Instrument "WFC3"
    -Pure_Par_Allowed 1
    -Cfg {"WFC3/UVIS"} -Mode {"ACCUM"} -Type "both" -String_Values {"FULL"}
    -Min_Val 16 -Max_Val 4142 -Increment 2 -Pure_Par_Allowed 1
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "CENTERAXIS2" -Instrument "WFC3"
    -Pure_Par_Allowed 1
    -Cfg {"WFC3/UVIS"} -Mode {"ACCUM"} -Type "both" -String_Values {"TARGET"}
    -Min_Val 9 -Max_Val 4093 -Increment 1 -Pure_Par_Allowed 1
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "CENTERAXIS1" -Instrument "WFC3"
    -Pure_Par_Allowed 1
    -Cfg {"WFC3/UVIS"} -Mode {"ACCUM"} -Type "both" -String_Values {"TARGET"}
    -Min_Val 11 -Max_Val 4137 -Increment 1 -Pure_Par_Allowed 1
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "INJECT" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"NONE" "YES" "CONT" "LINE10" "LINE17" "LINE25"} -Pure_Par_Allowed 1
    -Availability "caut-use"}

# Only NONE and YES are supported for INJECT, the other values are restricted
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}}
    -Result {{{"optional_parameter" "INJECT"} {"CONT" "LINE10" "LINE17" "LINE25"}}}
    -Availability "eng-only"
    -Message "For WFC3/UVIS ACCUM exposures in Available mode, INJECT can only be NONE or YES."}

Instrument_Optional_Parameter {-Name "BLADE" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"A" "B"} -Pure_Par_Allowed 1
    -Availability "caut-use"}

# BLADE=B is restricted (A is Available)
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}}
    -Result {{{"optional_parameter" "BLADE"} {"B"}}}
    -Availability "eng-only"
    -Message "BLADE B is a restricted value for WFC3/UVIS ACCUM"}


# BLADE exposures must be <60 sec
# check moved to ExposureSpecification.checkWfc3BladeExpTime
# Combination {-Type "illegal" -Instrument "WFC3"
#     -Condition {{"mode" "ACCUM"} {{"optional_parameter" "BLADE"} {"*"}}}
#     -Result {{"exp_time" {> 60}}}
#     -Message "BLADE is allowed only when exposure time is less than 60 sec."}
 
Instrument_Optional_Parameter {-Name "CTE" -Instrument "WFC3"
    -Cfg "WFC3/UVIS" -Mode "ACCUM" -Type "string"
    -String_Values {"NONE" "EPER"} -Pure_Par_Allowed 1 -Availability "eng-only"}


#
# WFC3/IR Optional Parameters
#
Instrument_Optional_Parameter {-Name "SAMP-SEQ" -Instrument "WFC3"
    -Cfg "WFC3/IR" -Mode "MULTIACCUM" -Type "string"
    -String_Values {"RAPID" "SPARS10" "SPARS25" "SPARS50" "SPARS100" "SPARS200" "STEP25" "STEP50" "STEP100" "STEP200" "STEP400" "MIF600" "MIF900" "MIF1200" "MIF1500"} -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "NSAMP" -Instrument "WFC3"
    -Cfg "WFC3/IR" -Mode "MULTIACCUM" -Type "numeric"
    -Min_Val 1 -Max_Val 15 -Increment 1 -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "GAIN" -Instrument "WFC3"
    -Cfg "WFC3/IR" -Mode "MULTIACCUM" -Type "string"
    -String_Values {"2.0" "2.5" "3.0" "4.0"} -Pure_Par_Allowed 1 -Availability "eng-only"}
#
# WFC3 Optional Parameters (plain WFC3, eng-only)
#

Instrument_Optional_Parameter {-Name "IRTEMP" -Instrument "WFC3"
    -Cfg {"WFC3"} -Mode "ANNEAL" -Type "string"
    -String_Values {"COLD" "WARM"} -Availability "eng-only"}

# IRTEMP is required for ANNEAL
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3"} {"mode" "ANNEAL"}}
    -Result {{{"optional_parameter" "IRTEMP"} {! "*"}}}
    -Message "IRTEMP must be specified for WFC3 ANNEAL mode."}


#
# WFC3/ALIGN Optional Parameters
#
Instrument_Optional_Parameter {-Name "FOCUS" -Instrument "WFC3"
    -Cfg {"WFC3/UVIS" "WFC3/IR"} -Mode "ALIGN" -Type "numeric"
    -Min_Val -11232 -Max_Val 11232 -Increment 1 -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "TILT" -Instrument "WFC3"
    -Cfg {"WFC3/UVIS" "WFC3/IR"} -Mode "ALIGN" -Type "string"
    -String_Values {"NO" "YES"} -Availability "eng-only"}

#
# Legal cfg/mode combinations
#
Combination {-Type "legal" -Instrument "WFC3" -Condition {{"cfg" {"WFC3/UVIS"}}}
    -Result {{"mode" {"ACCUM"}}}}
Combination {-Type "legal" -Instrument "WFC3" -Condition {{"cfg" {"WFC3/IR"}}}
    -Result {{"mode" {"MULTIACCUM"}}}}
Combination {-Type "legal" -Instrument "WFC3" -Condition {{"cfg" {"WFC3/UVIS" "WFC3/IR"}}}
    -Result {{"mode" {"ALIGN"}}}}
Combination {-Type "legal" -Instrument "WFC3" -Condition {{"cfg" {"WFC3"}}}
    -Result {{"mode" {"ANNEAL"}}}}

Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/UVIS"}} {"mode" "ACCUM"}}
    -Result {{"spectral_element" {"WFC3-UVIS-ACCUM-FILTERS"}}}}
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/UVIS"}} {"mode" "ACCUM"}}
    -Result {{"spectral_element" {"WFC3-UVIS-QUAD-FILTERS"}}}}
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/IR"}} {"mode" "MULTIACCUM"}}
    -Result {{"spectral_element" {"WFC3-IR-MULTIACCUM-FILTERS"}}}}
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/IR"}} {"mode" "MULTIACCUM"}}
    -Result {{"spectral_element" {"WFC3-IR-G-FILTERS"}}}}

Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" { "WFC3/UVIS"}} {"mode" {"ACCUM"}} {"spectral_element" {"WFC3-UVIS-ACCUM-FILTERS" "DEF"}}}
    -Result {{"aperture" {"WFC3-UVIS-ACCUM-APERTURES" "WFC3-UVIS-SUB-APERTURES"}}}}
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" { "WFC3/UVIS"}} {"mode" {"ACCUM"}} {"spectral_element" {"WFC3-UVIS-QUAD-FILTERS"}}}
    -Result {{"aperture" "WFC3-UVIS-QUAD-APERTURES"}}}
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" {"ACCUM"}} {"calibration_target" {"DARK" "DARK-NM" "BIAS"}}}
    -Result {{"spectral_element" "DEF"}}}
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/IR"}} {"mode" {"MULTIACCUM"}} {"spectral_element" {"WFC3-IR-MULTIACCUM-FILTERS"}}}
    -Result {{"aperture" "WFC3-IR-MULTIACCUM-APERTURES"}}}
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/IR"} {"mode" {"MULTIACCUM"}} {"calibration_target" {"DARK" "DARK-NM"}}}
    -Result {{"spectral_element" "BLANK"}}}

#
# illegal aperture/se settings
#
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "ACCUM"} {"spectral_element" "WFC3-UVIS-QUAD-FILTERS"}}
    -Result {{"aperture" {! "WFC3-UVIS-QUAD-APERTURES"}}}
    -Message "WFC3 QUAD filters may only be used with the UVIS-QUAD, UVIS-QUAD-FIX or UVIS-QUAD-SUB aperture."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"} {"spectral_element" "WFC3-UVIS-G-FILTERS"}}
    -Result {{"aperture" {! "UVIS"}}}
    -Message "WFC3 spectral element G280 must specify aperture UVIS."}


Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} {"spectral_element" "WFC3-IR-G-FILTERS"}}
    -Result {{"aperture" {! "IR" "WFC3-IR-SUB-NOT-FIX-APERTURES" "WFC3-IR-GRISM-APERTURES"}}} 
    -Message "WFC3 spectral element G102/G141 may specify aperture IR or IRSUB* or GRISM* but may not specifiy IRSUB*-FIX"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} {"spectral_element" "WFC3-IR-G-FILTERS"}}
    -Result {{"aperture" {"IR" "WFC3-IR-SUB-APERTURES"}}}
    -Availability "caut-use"
    -Message "WFC3 apertures IR and IRSUB* are only allowed for G102/G141 in Available mode."}


#
# illegal parameter settings
#

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "ACCUM"}}
    -Result {{{"optional_parameter" "GAIN"} {"8"}}}
    -Availability "eng-only"
    -Message "On WFC3, the value of 8 for the GAIN optional parameter is an engineering-only setting."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{{"optional_parameter" "GAIN"} {"16"}}}
    -Availability "eng-only"
    -Message "On WFC3, the value of 16 for the GAIN optional parameter is an engineering-only setting."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"}}
    -Result {{"exp_time" {> 3600}}}
    -Message "WFC3 exposures must not be longer than 3600 seconds."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS" } {"calibration_target" {"DARK" "BIAS"}}}
    -Result {{"spectral_element" {! "DEF"}}}
    -Message "WFC3/UVIS DARK and BIAS Targets must specify DEF for the Spectral Element."}
# note: DARK-NM allows spec elems besides DEF

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"} {"calibration_target" "BIAS"}}
    -Result {{"exp_time" {!= 0}}}
    -Message "WFC3/UVIS ACCUM mode exposures for target BIAS must use an exposure time of zero."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{{"optional_parameter" "CR-SPLIT"} {! "NO"}}}
    -Result {{"calibration_target" {"DARK" "DARK-NM" "BIAS" "DEUTERIUM" "TUNGSTEN"}}}
    -Message "CR-SPLIT must be NO or not specified on an internal exposure."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{{"optional_parameter" "BLADE"} {"*"}}}
    -Result {{"calibration_target" {"DARK" "DARK-NM" "BIAS"}}}
    -Message "BLADE may not be specified for the DARK, DARK-NM or BIAS internal targets."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"calibration_target" {"DEUTERIUM" "BIAS"}}}
    -Result {{{"optional_parameter" "CTE"}}}
    -Message "CTE Can't be used with a DEUTERIUM or BIAS targets."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"aperture" {! "UVIS"}}}
    -Result {{{"optional_parameter" "CTE"} {"EPER"}}}
    -Message "Aperture=UVIS is required when CTE=EPER."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{{"optional_parameter" "CTE"} {"EPER"}}}
    -Result {{{"optional_parameter" {"CR-SPLIT" "BIN" "SIZEAXIS1" "SIZEAXIS2" "CENTERAXIS1" "CENTERAXIS2" "AMP" "CURRENT" "INJECT"}}}}
    -Message "Only the GAIN optional Parameter can be used when CTE=EPER."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/UVIS" "WFC3/IR"}} {"mode" "ALIGN"}}
    -Result {{"calibration_target" {! "NONE"}}}
    -Message "WFC3 ALIGN exposures must have target NONE"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"mode" "MULTIACCUM"} {"calibration_target" {"DARK" "DARK-NM"}}}
    -Result {{"spectral_element" {! "BLANK"}}}
    -Message "Spectral element must be BLANK with DARK or DARK-NM target"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" {! "WFC3/UVIS"}}}
    -Result {{"calibration_target" {"BIAS" "DEUTERIUM"}}}
    -Message "Calibration Targets BIAS and DEUTERIUM can only be used with Config WFC3/UVIS." }

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"optional_parameter" "CURRENT"}}
    -Result {{"calibration_target" {! "DEUTERIUM"}}}
    -Message "CURRENT optional parameter must specify DEUTERIUM as the target." }

#Combination {-Type "illegal" -Instrument "WFC3"
#    -Condition {{"cfg" {"WFC3/IR"}}}
#    -Result {{"calibration_target" {"EARTH-CALIB"}}}
#    -Availability "eng-only"
#    -Message "Calibration Target EARTH-CALIB is restricted for mode WFC3/IR." }

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3"}} {"mode" {"ANNEAL"}}}
    -Result {{"calibration_target" {! "NONE"}}}
    -Message "Target must be NONE for WFC3 ANNEAL mode." }

#
# exposure times
#
Combination {-Type "legal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{"exp_time" {"DEF"}}}}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{"exp_time" {! "DEF"}}}
    -Message "All MULTIACCUM exposures must have an exposure time of DEF.  The sequence chosen with SAMP-SEQ and
        NSAMP will determine the exposure time."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{{"optional_parameter" "NSAMP"} {! "*"}}}
    -Message "You must specify NSAMP when using MULTIACCUM Mode."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{{"optional_parameter" "SAMP-SEQ"} {! "*"}}}
    -Message "You must specify SAMP-SEQ when using MULTIACCUM Mode."}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"}}
    -Result {{{"optional_parameter" "SAMP-SEQ"} {"MIF600" "MIF900" "MIF1200" "MIF1500"}}}
    -Message "MIF* SAMP-SEQs are Available but Unsupported."
    -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} 
	{"aperture" {"IRSUB64" "IRSUB512" "IRSUB64-FIX" "IRSUB512-FIX" 
	    "GRISM64" "GRISM512"}}}
    -Result {{{"optional_parameter" "SAMP-SEQ"} {"SPARS10"}}}
    -Message "SPARS10 SAMP-SEQ is Available but Unsupported for some IRSUB and GRISM apertures."
    -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} 
	{"aperture" {"IRSUB64" "IRSUB128" "IRSUB64-FIX" "IRSUB128-FIX" 
	    "GRISM64" "GRISM128"}}}
    -Result {{{"optional_parameter" "SAMP-SEQ"} {"SPARS25"}}}
    -Message "SPARS25 SAMP-SEQs is Available but Unsupported for some IRSUB and GRISM apertures."
    -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} 
	{"aperture" {"IRSUB64" "IRSUB128" "IRSUB256" "IRSUB64-FIX" "IRSUB128-FIX" "IRSUB256-FIX" 
	    "GRISM64", "GRISM128" "GRISM256"}}}
    -Result {{{"optional_parameter" "SAMP-SEQ"} {"STEP25"}}}
    -Message "STEP25 SAMP-SEQ is Available but Unsupported for some IRSUB and GRISM apertures."
    -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "MULTIACCUM"} 
	{"aperture" {"WFC3-IR-SUB-APERTURES" "WFC3-IR-GRISM-SUBS"}}}
    -Result {{{"optional_parameter" "SAMP-SEQ"} 
	{"SPARS50" "SPARS100" "SPARS200" "STEP50" "STEP100" "STEP200" "STEP400"}}}
    -Message "SPARS50-200, and STEP50-400 SAMP-SEQs are Available but Unsupported for all IRSUB and GRISM subapertures."
    -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "*"} {"mode" "ALIGN"}}
    -Result {{"exp_time" {< 0.0}}}
    -Message "WFC3 ALIGN exposures must be greater than 0.0 seconds."}
#
# SIZEAXIS[1-2] cannot be used on Subarray Aperture
#
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/UVIS"}} {"mode" "ACCUM"} {{"optional_parameter" "SIZEAXIS1"} {"*"}}}
    -Result {{"aperture" {"WFC3-UVIS-SUB-APERTURES" "UVIS-QUAD-SUB"}}}
    -Message "SIZEAXIS1 may not be specified if aperture is a Subarray Aperture." }

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/UVIS"}} {"mode" "ACCUM"} {{"optional_parameter" "SIZEAXIS2"} {"*"}}}
    -Result {{"aperture" {"WFC3-UVIS-SUB-APERTURES" "UVIS-QUAD-SUB"}}}
    -Message "SIZEAXIS2 may not be specified if aperture is a Subarray Aperture." }
#
# CENTERAXIS[1-2] can only be used in conjunction with SIZEAXIS[1-2]
#
Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/UVIS"}} {"mode" {"ACCUM"}} {{"optional_parameter" "CENTERAXIS1"} {"*"}}}
    -Result {{{"optional_parameter" "SIZEAXIS1"} {! "*"}}}
    -Message "CENTERAXIS1 may only be specified if SIZEAXIS1 is specifed." }

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" {"WFC3/UVIS"}} {"mode" {"ACCUM"}} {{"optional_parameter" "CENTERAXIS2"} {"*"}}}
    -Result {{{"optional_parameter" "SIZEAXIS2"} {! "*"}}}
    -Message "CENTERAXIS2 may only be specified if SIZEAXIS2 is specifed." }

Combination {-Type "illegal" -Instrument "WFC3"
    -Condition {{"cfg" "WFC3/UVIS"} {"mode" "ACCUM"} {{"optional_parameter" "CENTERAXIS2"} {> 2043}}}
    -Result {{{"optional_parameter" "CENTERAXIS2"} {< 2059}}}
    -Message "CENTERAXIS2 should be between 9 and 2043 inclusive or between 2059 and 4093 inclusive or TARGET."}

Combination {-Type "illegal" -Instrument "WFC3"
   -Condition {{"cfg" {"WFC3"}}}
   -Result {{"calibration_target" {! "NONE"}}}
   -Message "Only target NONE is allowed with config WFC3."}   
   
#######################################################################################
#
# Instrument COS
#
#######################################################################################
Print_If_Verbose "COS forms"
Instrument_Cfg {-Name "COS" -Instrument "COS" -Availability "eng-only"}
Instrument_Cfg {-Name "COS/NUV" -Instrument "COS"}
Instrument_Cfg {-Name "COS/FUV" -Instrument "COS"}

#
# COS Instrument Modes
#
Instrument_Mode {-Name "TIME-TAG" -Instrument "COS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "ACCUM" -Instrument "COS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "ACQ/SEARCH" -Instrument "COS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "ACQ/IMAGE" -Instrument "COS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "ACQ/PEAKXD" -Instrument "COS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "ACQ/PEAKD" -Instrument "COS" -Pure_Par_Allowed 1}
Instrument_Mode {-Name "ALIGN/APER" -Instrument "COS" -Availability "eng-only"}
Instrument_Mode {-Name "ALIGN/OSM" -Instrument "COS" -Availability "eng-only"}

#
# COS Apertures
#
Object_Set {-Name "COS-FUV-NUV-APERTURES" -Type "aperture"}
Object_Set {-Name "COS-FUV-NUV-TIMETAG-APERTURES" -Type "aperture"}

Instrument_Aperture {-Name "PSA" -Instrument "COS"
    -Object_Sets {"COS-FUV-NUV-APERTURES" "COS-FUV-NUV-TIMETAG-APERTURES"}}
Instrument_Aperture {-Name "BOA" -Instrument "COS"
    -Object_Sets {"COS-FUV-NUV-APERTURES" "COS-FUV-NUV-TIMETAG-APERTURES"}}
Instrument_Aperture {-Name "WCA" -Instrument "COS"
    -Object_Sets {"COS-FUV-NUV-TIMETAG-APERTURES"}}
Instrument_Aperture {-Name "FCA" -Instrument "COS"
    -Object_Sets {"COS-FUV-NUV-TIMETAG-APERTURES"}
    -Availability "eng-only"}
Instrument_Aperture {-Name "DEF" -Instrument "COS"}

#
# COS Spectral Elements
#
Object_Set {-Name "COS-FUV-FILTERS" -Type "spectral_element"}
Object_Set {-Name "COS-NUV-FILTERS" -Type "spectral_element"}
Object_Set {-Name "COS-NUV-MIRRORS" -Type "spectral_element"}

Instrument_Spectral_Element {-Name "G130M" -Instrument "COS"
    -Wave_List {1055 1096 1222 1291 1300 1309 1318 1327}
    -Object_Sets {"COS-FUV-FILTERS"}
    -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G140L" -Instrument "COS"
    -Wave_List {1105 1230 1280}
    -Object_Sets {"COS-FUV-FILTERS"}
    -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G160M" -Instrument "COS"
    -Wave_List {1577 1589 1600 1611 1623}
    -Object_Sets {"COS-FUV-FILTERS"}
    -Wheel "Wheel1"}

Instrument_Spectral_Element {-Name "G185M" -Instrument "COS"
    -Wave_List {1786 1817 1835 1850 1864 1882 1890 1900 1913 1921 1941 1953 1971 1986 2010}
    -Object_Sets {"COS-NUV-FILTERS"}
    -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G225M" -Instrument "COS"
    -Wave_List {2186 2217 2233 2250 2268 2283 2306 2325 2339 2357 2373 2390 2410}
    -Object_Sets {"COS-NUV-FILTERS"}
    -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G230L" -Instrument "COS"
    -Wave_List {2635 2950 3000 3360}
    -Object_Sets {"COS-NUV-FILTERS"}
    -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "G285M" -Instrument "COS"
    -Wave_List {2617 2637 2657 2676 2695 2709 2719 2739 2850 2952 2979 2996 3018 3035 3057 3074 3094}
    -Object_Sets {"COS-NUV-FILTERS"}
    -Wheel "Wheel1"}

Instrument_Spectral_Element {-Name "MIRRORA" -Instrument "COS"
    -Object_Sets {"COS-NUV-MIRRORS"}
    -Wheel "Wheel1"}
Instrument_Spectral_Element {-Name "MIRRORB" -Instrument "COS"
    -Object_Sets {"COS-NUV-MIRRORS"}
    -Wheel "Wheel1"}

Instrument_Spectral_Element {-Name "DEF" -Instrument "COS"}

#
# COS Optional Parameters
#
Instrument_Optional_Parameter {-Name "BUFFER-TIME" -Instrument "COS" -Mode "TIME-TAG"
    -Type "numeric" -Min_Val 80 -Max_Val 20000000 -Increment 1 -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "SEGMENT" -Instrument "COS"
    -Cfg {"COS/FUV"}
    -Mode {"ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD" "TIME-TAG" "ACCUM"} -Type "string"
    -String_Values {"BOTH" "A" "B"}
    -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "EXTENDED" -Instrument "COS"
    -Mode "TIME-TAG"
    -Type "string" -String_Values {"NO" "YES"}
    -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "EXTENDED" -Instrument "COS"
    -Mode "ACCUM"
    -Type "string" -String_Values {"NO" "YES"}
    -Pure_Par_Allowed 1}

Instrument_Optional_Parameter {-Name "STIM-RATE" -Instrument "COS"
    -Cfg "COS/FUV"
    -Mode "TIME-TAG"
    -Type "string" -String_Values {"DEF" "0" "2" "30" "2000"}
    -Pure_Par_Allowed 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "LIFETIME-POS" -Instrument "COS"
    -Type "string" -String_Values {"CURRENT" "ORIGINAL" "ALTERNATE" "DEF"}
    -Mode {"TIME-TAG" "ACCUM" "ACQ/SEARCH" "ACQ/IMAGE" "ACQ/PEAKXD" "ACQ/PEAKD"}
    # excludes  "ALIGN/APER" "ALIGN/OSM" 
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "STIM-RATE" -Instrument "COS"
    -Cfg "COS/FUV"
    -Mode "ACCUM"
    -Type "string" -String_Values {"DEF" "0" "2" "30" "2000"}
    -Pure_Par_Allowed 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "SCAN-SIZE" -Instrument "COS"
    -Mode "ACQ/SEARCH"
    -Pure_Par_Allowed 1
    -Type "numeric" -Min_Val 2 -Max_Val 5 -Increment 1}

Instrument_Optional_Parameter {-Name "STEP-SIZE" -Instrument "COS"
    -Mode "ACQ/SEARCH"
    -Pure_Par_Allowed 1
    -Type "numeric" -Min_Val 0.2 -Max_Val 2.0}

Instrument_Optional_Parameter {-Name "CENTER" -Instrument "COS"
    -Cfg "COS/FUV"
    -Mode "ACQ/SEARCH"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"DEF" "FLUX-WT" "FLUX-WT-FLR" "BRIGHTEST"}}

Instrument_Optional_Parameter {-Name "CENTER" -Instrument "COS"
    -Cfg "COS/NUV"
    -Mode "ACQ/SEARCH"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"DEF" "FLUX-WT" "FLUX-WT-FLR" "BRIGHTEST"}}

Instrument_Optional_Parameter {-Name "LOCAL-THRESHOLD" -Instrument "COS"
    -Mode {"ACQ/SEARCH" "ACQ/PEAKD"}
    -Type "numeric" -Min_Val 0 -Max_Val 64 -Increment 1
    -Pure_Par_Allowed 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "NUM-POS" -Instrument "COS" -Mode "ACQ/PEAKD"
    -Type "numeric"
    -Pure_Par_Allowed 1
    -Min_Val 3 -Max_Val 9 -Increment 2}

Instrument_Optional_Parameter {-Name "STEP-SIZE" -Instrument "COS"
    -Mode "ACQ/PEAKD"
    -Pure_Par_Allowed 1
    -Type "numeric" -Min_Val 0.01 -Max_Val 2.0}

Instrument_Optional_Parameter {-Name "CENTER" -Instrument "COS"
    -Cfg "COS/FUV"
    -Mode "ACQ/PEAKD"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"DEF" "FLUX-WT" "FLUX-WT-FLR" "BRIGHTEST"}}

Instrument_Optional_Parameter {-Name "STRIPE" -Instrument "COS"
    -Cfg {"COS/NUV"}
    -Mode "ACQ/PEAKXD" -Type "string"
    -Pure_Par_Allowed 1
    -String_Values {"DEF" "SHORT" "MEDIUM" "LONG"}}

Instrument_Optional_Parameter {-Name "CENTER" -Instrument "COS"
    -Cfg "COS/NUV"
    -Mode "ACQ/PEAKD"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"DEF" "FLUX-WT-FLR" "FLUX-WT" "BRIGHTEST"}}

Instrument_Optional_Parameter {-Name "XAPER" -Instrument "COS"
    -Mode {"ALIGN/APER"}
    -Type "numeric" -Min_Val -560 -Max_Val 560 -Increment 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "YAPER" -Instrument "COS"
    -Mode {"ALIGN/APER"}
    -Type "numeric" -Min_Val -200 -Max_Val 200 -Increment 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "FOCUS" -Instrument "COS"
    -Mode {"ALIGN/OSM"}
    -Type "numeric" -Min_Val -2000 -Max_Val 2000 -Increment 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "OSM1ROT" -Instrument "COS"
    -Mode {"ALIGN/OSM"}
    -Type "numeric" -Min_Val -600 -Max_Val 600 -Increment 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "OSM2ROT" -Instrument "COS"
    -Mode {"ALIGN/OSM"}
    -Type "numeric" -Min_Val -700 -Max_Val 700 -Increment 1
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "FP-POS" -Instrument "COS"
    -Cfg {"COS/FUV" "COS/NUV"}
    -Mode {"ACCUM" "TIME-TAG"}
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"ALL" "1" "2" "3" "4"}}

Instrument_Optional_Parameter {-Name "FLASH" -Instrument "COS"
    -Cfg {"COS/FUV" "COS/NUV"}
    -Mode {"TIME-TAG"}
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"YES" "NO" "*"}}

Instrument_Optional_Parameter {-Name "WAVECAL" -Instrument "COS"
    -Cfg {"COS/FUV" "COS/NUV"}
    -Mode {"ACCUM" "TIME-TAG"}
    -Type "string" -String_Values {"YES" "NO"}
    -Pure_Par_Allowed 1
    -Availability "eng-only" }

Instrument_Optional_Parameter {-Name "CURRENT" -Instrument "COS"
    -Cfg  {"COS/FUV" "COS/NUV"}
    -Mode {"TIME-TAG"}
    -Type "string" -String_Values {"DEF" "LOW" "MEDIUM" "HIGH"}
    -Pure_Par_Allowed 1 -Availability "eng-only" }
#
# COS Legal cfg/mode combinations
#
Combination {-Type "legal" -Instrument "COS" -Condition {{"cfg" {"COS"}}}
    -Result {{"mode" {"ALIGN/APER" "ALIGN/OSM"}}}}
Combination {-Type "legal" -Instrument "COS" -Condition {{"cfg" {"COS/NUV" "COS/FUV"}}}
    -Result {{"mode" {"TIME-TAG" "ACCUM" "ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD"}}}}
Combination {-Type "legal" -Instrument "COS" -Condition {{"cfg" {"COS/NUV"}}}
    -Result {{"mode" {"ACQ/IMAGE"}}}}

Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" { "COS/NUV"}} {"mode" {"TIME-TAG"}}
        {"spectral_element" {"COS-NUV-FILTERS"}}}
    -Result {{"aperture" "COS-FUV-NUV-TIMETAG-APERTURES"}}}
Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" { "COS/NUV"}} {"mode" {"ACCUM" "ACQ/SEARCH" "ACQ/IMAGE" "ACQ/PEAKXD" "ACQ/PEAKD"}}
        {"spectral_element" {"COS-NUV-FILTERS"}}}
    -Result {{"aperture" "COS-FUV-NUV-APERTURES"}}}

Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" { "COS/FUV"}} {"mode" {"TIME-TAG"}}
        {"spectral_element" {"COS-FUV-FILTERS"}}}
    -Result {{"aperture" "COS-FUV-NUV-TIMETAG-APERTURES"}}}
Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" { "COS/FUV"}} {"mode" {"ACCUM" "ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD"}}
        {"spectral_element" {"COS-FUV-FILTERS"}}}
    -Result {{"aperture" "COS-FUV-NUV-APERTURES"}}}

Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" { "COS/NUV"}} {"mode" {"TIME-TAG"}}
        {"spectral_element" {"COS-NUV-MIRRORS"}}}
    -Result {{"aperture" "COS-FUV-NUV-TIMETAG-APERTURES"}}}
Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" { "COS/NUV"}} {"mode" {"ACCUM" "ACQ/SEARCH" "ACQ/IMAGE"}}
        {"spectral_element" {"COS-NUV-MIRRORS"}}}
    -Result {{"aperture" "COS-FUV-NUV-APERTURES"}}}


#
# COS Legal cfg/spectral_element combinations, and mode/spectral_element combinations
#
Combination {-Type "legal" -Instrument "COS" -Condition {{"cfg" "COS/NUV"}
    {"mode" {"TIME-TAG" "ACCUM" "ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD"}}}
    -Result {{"spectral_element" "COS-NUV-FILTERS"}}}
Combination {-Type "legal" -Instrument "COS" -Condition {{"cfg" "COS/NUV"}
    {"mode" {"ACCUM" "ACQ/SEARCH" "ACQ/IMAGE" "TIME-TAG"}}}
    -Result {{"spectral_element" "COS-NUV-MIRRORS"}}}
Combination {-Type "legal" -Instrument "COS" -Condition {{"cfg" "COS/FUV"}
    {"mode" {"TIME-TAG" "ACCUM" "ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD"}}}
    -Result {{"spectral_element" "COS-FUV-FILTERS"}}}

Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" "COS/NUV"} {"mode" {"TIME-TAG"}} {"calibration_target" {"DARK"}}}
    -Result {{"spectral_element" "DEF"}}}
Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" "COS/NUV"} {"mode" {"TIME-TAG"}} {"calibration_target" {"DARK"}}}
    -Result {{"aperture" "DEF"}}}
Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" "COS/FUV"} {"mode" {"TIME-TAG"}} {"calibration_target" {"DARK"}}}
    -Result {{"spectral_element" "DEF"}}}
Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" "COS/FUV"} {"mode" {"TIME-TAG"}} {"calibration_target" {"DARK"}}}
    -Result {{"aperture" "DEF"}}}

#
# COS Illegal Optional Parameters
#
Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"ACQ/SEARCH"}}
	{{"optional_parameter" "CENTER"} {"FLUX-WT-FLR"}}}
    -Result {{{"optional_parameter" "SCAN-SIZE"} "2"}}
    -Message "SCAN-SIZE=2 is not allowed with CENTER=FLUX-WT-FLR for COS ACQ/SEARCH"}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"ACQ/SEARCH"}}}
    -Result {{{"optional_parameter" "SCAN-SIZE"} {! "*"}}}
    -Message "COS ACQ/SEARCH mode must have a SCAN-SIZE optional parameter"}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"calibration_target" {"DARK" "NONE" "DEUTERIUM"}}}
    -Result {{{"optional_parameter" "FLASH"} {"*"}}}
    -Message "COS FLASH may not be specified on an internal target"}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"calibration_target" {"WAVE"}}}
    -Result {{{"optional_parameter" "FLASH"} {"*"}}}
    -Availability "eng-only"
    -Message "COS FLASH when used with WAVE is Restricted."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"aperture" {"BOA"}}}
    -Result {{{"optional_parameter" "FLASH"} {"*"}}}
    -Message "COS FLASH cannot be used with BOA aperture."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/FUV" "COS/NUV"}}}
    -Result {{{"optional_parameter" "FLASH"} {! "YES" "NO"}}}
    -Availability "eng-only"
    -Message "Values other than YES and NO are Restricted for COS FLASH."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{{"optional_parameter" "LOCAL-THRESHOLD"} {"*"}}}
    -Result {{{"optional_parameter" "CENTER"} {"BRIGHTEST"}}}
    -Message "LOCAL-THRESHOLD is not allowed when CENTER=BRIGHTEST"}

#
# exposure times
#
Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"ACQ/SEARCH" "ACQ/IMAGE" "ACQ/PEAKXD" "ACQ/PEAKD"}}}
    -Result {{"exp_time" {> 6500}}}
    -Message "COS ACQ/* exposures must be less than 6500 seconds."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"ALIGN/APER" "ALIGN/OSM"}}}
    -Result {{"exp_time" {< 0}}}
    -Message "COS exposures must be greater than 0.0  seconds."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"ACQ/SEARCH" "ACQ/IMAGE" "ACQ/PEAKXD" "ACQ/PEAKD"}}}
    -Result {{"exp_time" {< 0.1}}}
    -Message "COS exposures in the specified mode must be greater than 0.1 seconds."}

Combination {-Type "legal" -Instrument "COS"
    -Condition {{"cfg" "*"} {"mode" "TIME-TAG"} {"calibration_target" {"WAVE"}}}
    -Result {{"exp_time" {"DEF"}}}}
    
Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" "*"} {"mode" "TIME-TAG"} {"calibration_target" {! "WAVE"}}}
    -Result {{"exp_time" {"DEF"}}}}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" "*"} {"mode" "TIME-TAG"} {"calibration_target" {"WAVE"}}}
    -Result {{"exp_time" {! "DEF"}}}
    -Availability "caut-use"
    -Message "All COS TIME-TAG exposures must have an exposure time of DEF for Target Name = WAVE."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"calibration_target" {"DARK"}}}
    -Result {{"spectral_element" {! "DEF"}}}
    -Message "COS DARK Targets must specify DEF for the Spectral Element."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/FUV" "COS/NUV"}}
        {"spectral_element" {"COS-NUV-TIME-TAG-FILTERS" "COS-FUV-TIME-TAG-FILTERS"}}}
    -Result {{{"wavelength" {! "*"}}}}
    -Message "Specification of wavelength is required with the specified spectral element."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/NUV"}}
        {"spectral_element" {"COS-NUV-MIRRORS"}}}
    -Result {{{"wavelength" {"*"}}}}
    -Message "Specification of wavelength is not allowed with the MIRRORs."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" "COS/NUV"}  {"mode" "TIME-TAG"} {"calibration_target" {"DEUTERIUM"}}}
    -Result {{{"spectral_element" {"COS-NUV-MIRRORS"}}}}
    -Message "The selected Spectral Element is illegal for this configuration when the target is Deuterium."}

#
# Added the following constraint in support of OPR 42477
# Frank Tanner - January, 2001
#
Combination {-Type "illegal" -Instrument "COS"
    -Result {{"special_requirement" "FORMAT"}}
    -Message "FORMAT special requirement should not be used with COS"
    -Message "The COS requires telemetry through the engineering data channel.
Therefore, additional telemetry cannot be requested via the FORMAT special
requirement."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/FUV" "COS/NUV" "COS"}}
       {"mode" {"ACCUM" "ACQ/SEARCH" "ACQ/IMAGE" "ACQ/PEAKXD" "ACQ/PEAKD" "ALIGN/APER" "ALIGN/OSM"}}}
    -Result {{"calibration_target" {"DARK" "WAVE" "DEUTERIUM"}}}
    -Message "COS ACCUM, ALIGN, and ACQ mode exposures may not use Internal targets."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/FUV" "COS/NUV"}}
       {"mode" {"ACCUM" "ACQ/SEARCH" "ACQ/IMAGE" "ACQ/PEAKXD" "ACQ/PEAKD" "TIME-TAG"}}}
    -Result {{"calibration_target" {"NONE"}}}
    -Message "COS ACCUM, TIME-TAG, and ACQ mode exposures may not use target NONE."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"ACQ/PEAKD"}}}
    -Result {{{"optional_parameter" "STEP-SIZE"} {! "*"}}}
    -Message "COS ACQ/PEAKD mode must have a STEP-SIZE optional parameter"}

Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"cfg" {"COS/NUV"}} {"mode" "ACQ/PEAKXD"} {"spectral_element" {"G230L"}} }
   -Result {{{"optional_parameter" "STRIPE"} {"LONG"}}}
   -Message "STRIPE=LONG is not allowed with the G230L grating."}

Combination {-Type "illegal" -Instrument "COS" 
    -Condition {{"cfg" {"COS/FUV"}}  {"mode" "ACQ/PEAKXD"} }
    -Result {{{"optional_parameter" "SEGMENT"} "B"}}
    -Message "SEGMENT=B is restricted in COS/FUV ACQ/PEAKXD mode."
    -Availability "eng-only"}

Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"cfg" {"COS/NUV"}} {"mode" "ACQ/PEAKXD"} {"spectral_element" {"G230L"}} {"wavelength" {2635}}}
   -Result {{{"optional_parameter" "STRIPE"} {"SHORT"}}}
   -Message "STRIPE=SHORT is not allowed with the G230L grating and Wavelength = 2635."}

Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"cfg" {"COS/NUV"}} {"mode" "ACQ/PEAKXD"} {"spectral_element" {"G230L"}} {"wavelength" {3360}}}
   -Result {{{"optional_parameter" "STRIPE"} {"MEDIUM"}}}
   -Message "STRIPE=MEDIUM is not allowed with the G230L grating and Wavelength = 3360."}
#
# SEGMENT=A is default and only legal value for Grating = G140L and wavelength = 1105.
#
Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"cfg" {"COS/FUV"}} {"mode" {"ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD" "TIME-TAG" "ACCUM"}} {"spectral_element" {"G140L"}} {"wavelength" {1105}}}
   -Result {{{"optional_parameter" "SEGMENT"} {"B" "BOTH"}}}
    -Message "SEGMENT=A is the default and only allowed value with the G140L grating and Wavelength = 1105."}

# TODO added for 64267. probably obsolete now that 1230 is restricted (noted during PR 67599)
Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"cfg" {"COS/FUV"}} {"spectral_element" {"G140L"}} {"wavelength" {1230}}
       {{"optional_parameter" "FP-POS"} {"4" "ALL"}}}
   -Result {{{"optional_parameter" "SEGMENT"} {"B" "BOTH"}}}
   -Message "SEGMENT=A is required with the G140L grating and Wavelength = 1230 for FP-POS=4 or ALL."
   -Availability "eng-only"}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/FUV"}} {"mode" {"ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD"}}
       {"spectral_element" {"G140L"}} {"wavelength" {1230}}}
   -Result {{{"optional_parameter" "SEGMENT"} {"B"}}}
   -Message "SEGMENT=B is not allowed for FUV target acquisition modes for the G140L spectral element and Wavelength = 1230."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/FUV"}} {"mode" {"ACQ/SEARCH" "ACQ/PEAKXD" "ACQ/PEAKD"}}
       {"spectral_element" {"G140L"}} {"wavelength" {1280}}}
   -Result {{{"optional_parameter" "SEGMENT"} {"B"}}}
   -Message "SEGMENT=B is Restricted for FUV target acquisition modes for the G140L spectral element and Wavelength = 1280."
   -Availability "eng-only"}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"cfg" {"COS/FUV"}} {"mode" {"TIME-TAG"}}
	{"spectral_element" {"G130M"}} {"wavelength" {1055 1096}}
	{{"optional_parameter" "SEGMENT"} {"B"}}}
    -Result {{{"optional_parameter" "FLASH"} {"YES"}}}
    -Message "FLASH=YES is Restricted for FUV time-tag mode for the G130M spectral element with Wavelength = 1055 or 1096 and op SEGMENT=B."
    -Availability "eng-only"}




Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"spectral_element" {"G140L"}}}
   -Result {{"wavelength" {1230}}}
   -Message "Wavelength=1230 is Available but Unsupported.  It was made restricted beginning in cycle 18."
   -Availability "caut-use"}

Combination {-Type "illegal" -Instrument "COS" -Condition {{"cfg" "COS/FUV"}
    {"mode" {! "TIME-TAG" "ACCUM"}} {"spectral_element" "G130M"}}
    -Result {{"wavelength" {1055 1096 1222}}}
   -Message "Cannot use wavelengths 1055, 1096, or 1222 for ACQ mode."}
   
Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"ALIGN/APER" "ALIGN/OSM"}}}
    -Result {{"calibration_target" {! "NONE"}}}
    -Message "COS ALIGN modes must specify NONE as the target."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{{"optional_parameter" "FP-POS"} "*"}}
    -Result {{"calibration_target" {"DARK"}}}
    -Message "FP-POS may only be specified on External Targets or Internal Target = WAVE or DEUTERIUM."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{{"optional_parameter" "FP-POS"} {"ALL"}}}
    -Result {{"calibration_target" {"WAVE" "DEUTERIUM"}}}
    -Message "FP-POS may not be set to ALL on Internal Targets WAVE or DEUTERIUM."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"spectral_element" "COS-NUV-MIRRORS"}}
    -Availability "eng-only"
    -Result {{{"optional_parameter" "FP-POS"} "*"}}
    -Message "FP-POS is restricted for use with the MIRRORs."}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"TIME-TAG"}} {"calibration_target" {"DEUTERIUM"}}}
    -Result {{"aperture" {! "FCA"}}}
    -Message "Aperture must be FCA for Target Name = DEUTERIUM"}

Combination {-Type "illegal" -Instrument "COS"
    -Condition {{"mode" {"TIME-TAG"}} {"aperture" {"FCA"}}}
    -Result {{"calibration_target" {! "DEUTERIUM"}}}
    -Message "Calibration Target must be DEUTERIUM for Aperture FCA"}

Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"cfg" {"COS/NUV"}} {"mode" {"TIME-TAG"}} {"calibration_target" {"WAVE"}}}
   -Result {{"spectral_element" {"MIRRORA" "MIRRORB"}}}
   -Availability "eng-only"
   -Message "Spectral Elements MIRRORA, MIRRORB are available for Engineering Only when Config = COS/NUV, Mode = TIME-TAG, Target = WAVE."}
   
Combination {-Type "illegal" -Instrument "COS"
   -Condition {{"cfg" {"COS"}}}
   -Result {{"calibration_target" {! "NONE"}}}
   -Message "Only target NONE is allowed with config COS."}   
   
#######################################################################################
#
# Instrument ACS
#
#######################################################################################
Print_If_Verbose "ACS forms"
Instrument_Cfg {-Name "ACS/WFC" -Instrument "ACS" -Pure_Par_Allowed 1}
Instrument_Cfg {-Name "ACS/HRC" -Instrument "ACS" -Pure_Par_Allowed 1 -Availability "eng-only"}
Instrument_Cfg {-Name "ACS/SBC" -Instrument "ACS"}
Instrument_Cfg {-Name "ACS"     -Instrument "ACS" -Availability "eng-only"}

Instrument_Mode { -Name "ACCUM"  -Instrument "ACS" -Pure_Par_Allowed 1}
Instrument_Mode { -Name "ACQ"    -Instrument "ACS"}
Instrument_Mode { -Name "ANNEAL" -Instrument "ACS" -Availability "eng-only"}
Instrument_Mode { -Name "ALIGN"  -Instrument "ACS" -Availability "eng-only"}

#
# Aperture Object Sets
#
Object_Set {-Name "ACS-WFC"           -Type "aperture"}
Object_Set {-Name "ACS-WFC-SMALL"     -Type "aperture"}
Object_Set {-Name "ACS-WFC-IRAMP"     -Type "aperture"}
Object_Set {-Name "ACS-WFC-MRAMP"     -Type "aperture"}
Object_Set {-Name "ACS-WFC-ORAMP"     -Type "aperture"}
Object_Set {-Name "ACS-WFC1-QUADRANT" -Type "aperture"}
Object_Set {-Name "ACS-WFC2-QUADRANT" -Type "aperture"}
Object_Set {-Name "ACS-HRC"           -Type "aperture"}
Object_Set {-Name "ACS-HRC-ACQ"       -Type "aperture"}
Object_Set {-Name "ACS-HRC-CORON"     -Type "aperture"}
Object_Set {-Name "ACS-SBC"           -Type "aperture"}
Object_Set {-Name "ACS-SUBARRAY"      -Type "aperture"}

#
# Supported apertures
#
Instrument_Aperture {-Name "WFC"      -Instrument "ACS" -Object_Sets {"ACS-WFC-SMALL"}}
Instrument_Aperture {-Name "WFC1"     -Instrument "ACS" -Object_Sets {"ACS-WFC-SMALL"}}
Instrument_Aperture {-Name "WFC1-CTE" -Instrument "ACS" -Object_Sets {"ACS-WFC"}}
Instrument_Aperture {-Name "WFC2"     -Instrument "ACS" -Object_Sets {"ACS-WFC-SMALL"}}
Instrument_Aperture {-Name "WFC-FIX"  -Instrument "ACS" -Object_Sets {"ACS-WFC"}}
Instrument_Aperture {-Name "WFC1-FIX" -Instrument "ACS" -Object_Sets {"ACS-WFC"}}
Instrument_Aperture {-Name "WFC2-FIX" -Instrument "ACS" -Object_Sets {"ACS-WFC"}}
Instrument_Aperture {-Name "WFCENTER" -Instrument "ACS" -Object_Sets {"ACS-WFC"}}

Instrument_Aperture {-Name "WFC1-512"   -Instrument "ACS"  -Object_Sets {"ACS-WFC" "ACS-SUBARRAY"}}
Instrument_Aperture {-Name "WFC1-1K"    -Instrument "ACS"  -Object_Sets {"ACS-WFC" "ACS-SUBARRAY"}}
Instrument_Aperture {-Name "WFC1-2K"    -Instrument "ACS"  -Object_Sets {"ACS-WFC" "ACS-SUBARRAY"}}
Instrument_Aperture {-Name "WFC2-2K"    -Instrument "ACS"  
    -Object_Sets {"ACS-WFC" "ACS-SUBARRAY"} -Availability "caut-use"}

Instrument_Aperture {-Name "WFC1-IRAMP" -Instrument "ACS"  -Object_Sets {"ACS-WFC-IRAMP"}}
Instrument_Aperture {-Name "WFC1-MRAMP" -Instrument "ACS"  -Object_Sets {"ACS-WFC-MRAMP"}}
Instrument_Aperture {-Name "WFC2-MRAMP" -Instrument "ACS"  -Object_Sets {"ACS-WFC-MRAMP"}}
Instrument_Aperture {-Name "WFC2-ORAMP" -Instrument "ACS"  -Object_Sets {"ACS-WFC-ORAMP"}}

Instrument_Aperture {-Name "WFC1-IRAMPQ" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-IRAMP" "ACS-SUBARRAY" "ACS-WFC1-QUADRANT"}}
Instrument_Aperture {-Name "WFC1-MRAMPQ" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-MRAMP" "ACS-SUBARRAY" "ACS-WFC1-QUADRANT"}}
Instrument_Aperture {-Name "WFC2-MRAMPQ" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-MRAMP" "ACS-SUBARRAY" "ACS-WFC2-QUADRANT"} -Availability "caut-use"}
Instrument_Aperture {-Name "WFC2-ORAMPQ" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-ORAMP" "ACS-SUBARRAY" "ACS-WFC2-QUADRANT"}}

Instrument_Aperture {-Name "HRC"           -Instrument "ACS"  -Object_Sets {"ACS-HRC"}}
Instrument_Aperture {-Name "HRC-FIX"       -Instrument "ACS"  -Object_Sets {"ACS-HRC"}}
Instrument_Aperture {-Name "HRC-ACQ"       -Instrument "ACS"  -Object_Sets {"ACS-HRC-ACQ"}}
Instrument_Aperture {-Name "HRC-OCCULT0.8" -Instrument "ACS"  -Object_Sets {"ACS-HRC-CORON"}}
Instrument_Aperture {-Name "HRC-CORON1.8"  -Instrument "ACS"  -Object_Sets {"ACS-HRC-CORON"}}
Instrument_Aperture {-Name "HRC-CORON3.0"  -Instrument "ACS"  -Object_Sets {"ACS-HRC-CORON"}}

Instrument_Aperture {-Name "HRC-512"       -Instrument "ACS"  -Object_Sets {"ACS-HRC" "ACS-SUBARRAY"}}
Instrument_Aperture {-Name "HRC-SUB1.8"    -Instrument "ACS"  -Object_Sets {"ACS-HRC" "ACS-SUBARRAY"}}

Instrument_Aperture {-Name "SBC"     -Instrument "ACS"  -Object_Sets {"ACS-SBC"}}
Instrument_Aperture {-Name "SBC-FIX" -Instrument "ACS"  -Object_Sets {"ACS-SBC"}}

#
# Spectral Element Object Sets
#
Object_Set {-Name "ACS-WFC-FILTERS"         -Type "spectral_element"}
Object_Set {-Name "ACS-WFC-SMALL-FILTERS"   -Type "spectral_element"}
Object_Set {-Name "ACS-RAMP-FILTERS"        -Type "spectral_element"}
Object_Set {-Name "ACS-IRAMP-FILTERS"       -Type "spectral_element"}
Object_Set {-Name "ACS-MRAMP-FILTERS"       -Type "spectral_element"}
Object_Set {-Name "ACS-ORAMP-FILTERS"       -Type "spectral_element"}
Object_Set {-Name "ACS-HRC-FILTERS"         -Type "spectral_element"}
Object_Set {-Name "ACS-SBC-FILTERS"         -Type "spectral_element"}
#
# Spectral Elements per Wheel (Used by APT-OCM only)
#
Object_Set {-Name "ACS-FILTERS-1"       -Type "spectral_element"}
Object_Set {-Name "ACS-FILTERS-2"       -Type "spectral_element"}
Object_Set {-Name "ACS-ACQ-FILTERS-2"       -Type "spectral_element"}
Object_Set {-Name "ACS-POLARIZERS-1"        -Type "spectral_element"}
Object_Set {-Name "ACS-POLARIZERS-2"        -Type "spectral_element"}
#
Object_Set {-Name "ACS-PRISMS"          -Type "spectral_element"}
Object_Set {-Name "ACS-GRISMS"          -Type "spectral_element"}
Object_Set {-Name "ACS-POL-FILTERS"         -Type "spectral_element"}
Object_Set {-Name "ACS-POL-RAMPS"       -Type "spectral_element"}

#
# Spectral Elements
#
Instrument_Spectral_Element {-Name "DEF" -Instrument "ACS"}

Instrument_Spectral_Element {-Name "CLEAR" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS"}
    -Cfg {"ACS/WFC" "ACS/HRC"} -Availability "caut-use"}

#
# Wheel1
#
Instrument_Spectral_Element {-Name "F555W" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F775W" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F625W" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F550M" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F850LP" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "POL0UV" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-POLARIZERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "POL60UV" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-POLARIZERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "POL120UV" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-POLARIZERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F892N" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F606W" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F502N" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "G800L" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-GRISMS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F658N" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }

Instrument_Spectral_Element {-Name "F475W" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-1"}
    -Wheel "Wheel1" }
#
# Wheel2
#
Instrument_Spectral_Element {-Name "F660N" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-2" "ACS-ACQ-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "F814W" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-2" "ACS-ACQ-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "FR388N" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-MRAMP-FILTERS" "ACS-RAMP-FILTERS" "ACS-POL-RAMPS" "ACS-FILTERS-2"}
    -Wheel "Wheel2" -Min_Wave 3710 -Max_Wave 4049}

Instrument_Spectral_Element {-Name "FR423N" -Instrument "ACS"
    -Object_Sets {"ACS-IRAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 4049 -Max_Wave 4420}

Instrument_Spectral_Element {-Name "FR462N" -Instrument "ACS"
    -Object_Sets {"ACS-ORAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 4420 -Max_Wave 4824}

Instrument_Spectral_Element {-Name "F435W" -Instrument "ACS"
    -Object_Sets {"ACS-WFC-FILTERS" "ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-2" "ACS-ACQ-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "FR656N" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-MRAMP-FILTERS" "ACS-RAMP-FILTERS" "ACS-POL-RAMPS" "ACS-FILTERS-2"}
    -Wheel "Wheel2" -Min_Wave 6274 -Max_Wave 6848}

Instrument_Spectral_Element {-Name "FR716N" -Instrument "ACS"
    -Object_Sets {"ACS-IRAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 6848 -Max_Wave 7474}

Instrument_Spectral_Element {-Name "FR782N" -Instrument "ACS"
    -Object_Sets {"ACS-ORAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 7474 -Max_Wave 8158}

Instrument_Spectral_Element {-Name "POL0V" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-POLARIZERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "F330W" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-2" "ACS-ACQ-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "POL60V" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-POLARIZERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "F250W" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-2" "ACS-ACQ-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "POL120V" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-POLARIZERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "PR200L" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-PRISMS" "ACS-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "F344N" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-2" "ACS-ACQ-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "F220W" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-POL-FILTERS" "ACS-FILTERS-2"}
    -Wheel "Wheel2" }

Instrument_Spectral_Element {-Name "FR853N" -Instrument "ACS"
    -Object_Sets {"ACS-IRAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 8158 -Max_Wave 8905}

Instrument_Spectral_Element {-Name "FR931N" -Instrument "ACS"
    -Object_Sets {"ACS-ORAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 8905 -Max_Wave 9719}

Instrument_Spectral_Element {-Name "FR1016N" -Instrument "ACS"
    -Object_Sets {"ACS-ORAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 9719 -Max_Wave 10609}

Instrument_Spectral_Element {-Name "FR459M" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-MRAMP-FILTERS" "ACS-RAMP-FILTERS" "ACS-POL-RAMPS" "ACS-FILTERS-2"}
    -Wheel "Wheel2" -Min_Wave 3810 -Max_Wave 5366}

Instrument_Spectral_Element {-Name "FR647M" -Instrument "ACS"
    -Object_Sets {"ACS-IRAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 5366 -Max_Wave 7574}

Instrument_Spectral_Element {-Name "FR914M" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-MRAMP-FILTERS" "ACS-RAMP-FILTERS" "ACS-POL-RAMPS" "ACS-FILTERS-2"}
    -Wheel "Wheel2" -Min_Wave 7574 -Max_Wave 10709}

Instrument_Spectral_Element {-Name "FR505N" -Instrument "ACS"
    -Object_Sets {"ACS-HRC-FILTERS" "ACS-MRAMP-FILTERS" "ACS-RAMP-FILTERS" "ACS-POL-RAMPS" "ACS-FILTERS-2"}
    -Wheel "Wheel2" -Min_Wave 4824 -Max_Wave 5266}

Instrument_Spectral_Element {-Name "FR551N" -Instrument "ACS"
    -Object_Sets {"ACS-IRAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 5266 -Max_Wave 5748}

Instrument_Spectral_Element {-Name "FR601N" -Instrument "ACS"
    -Object_Sets {"ACS-ORAMP-FILTERS" "ACS-RAMP-FILTERS"}
    -Wheel "Wheel2" -Min_Wave 5748 -Max_Wave 6274}
#
# Wheel3
#
Instrument_Spectral_Element {-Name "F115LP" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS"}
    -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F125LP" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS"}
    -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F140LP" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS"}
    -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F150LP" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS"}
    -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F165LP" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS"}
    -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "F122M" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS"}
    -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "PR130L" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS" "ACS-PRISMS"}
    -Wheel "Wheel3"}
Instrument_Spectral_Element {-Name "PR110L" -Instrument "ACS"
    -Object_Sets {"ACS-SBC-FILTERS" "ACS-PRISMS"}
    -Wheel "Wheel3"}
#
# Optional Parameters
#
Instrument_Optional_Parameter {-Name "CR-SPLIT" -Instrument "ACS"  -Mode "ACCUM"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"NO" "2" "3" "4" "5" "6" "7" "8"} }

Instrument_Optional_Parameter {-Name "GAIN" -Instrument "ACS" -Cfg "ACS/WFC" -Mode "ACCUM"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"0.5" "1.0" "1.4" "2.0"}}

Instrument_Optional_Parameter {-Name "GAIN" -Instrument "ACS" -Cfg "ACS/HRC" -Mode "ACCUM"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"1" "2" "4" "8"}}

Instrument_Optional_Parameter {-Name "GAIN" -Instrument "ACS" -Cfg "ACS/HRC" -Mode "ACQ"
    -Pure_Par_Allowed 1
    -Type "string" -String_Values {"1" "2" "4" "8"}
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "SIZEAXIS2" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/WFC"} -Mode {"ACCUM"} -Type "both" -String_Values {"FULL"}
    -Min_Val 16 -Max_Val 2046
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "SIZEAXIS1" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/WFC"} -Mode {"ACCUM"} -Type "both" -String_Values {"FULL"}
    -Min_Val 16 -Max_Val 4140 -Increment 2
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "SIZEAXIS2" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/HRC"} -Mode {"ACCUM"} -Type "both" -String_Values {"FULL"}
    -Min_Val 16 -Max_Val 1022
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "SIZEAXIS1" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/HRC"} -Mode {"ACCUM"} -Type "both" -String_Values {"FULL"}
    -Min_Val 16 -Max_Val 1058 -Increment 2
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "CENTERAXIS2" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/WFC"} -Mode {"ACCUM"} -Type "both" -String_Values {"TARGET"}
    -Min_Val 9 -Max_Val 4087
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "CENTERAXIS1" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/WFC"} -Mode {"ACCUM"} -Type "both" -String_Values {"TARGET"}
    -Min_Val 11 -Max_Val 4135
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "CENTERAXIS2" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/HRC"} -Mode {"ACCUM"} -Type "both" -String_Values {"TARGET"}
    -Min_Val 9 -Max_Val 1015
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "CENTERAXIS1" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/HRC"} -Mode {"ACCUM"} -Type "both" -String_Values {"TARGET"}
    -Min_Val 11 -Max_Val 1053
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "COMPRESSION" -Instrument "ACS" -Cfg {"ACS/WFC"}
    -Pure_Par_Allowed 1
    -Mode "ACCUM" -Type "both" -String_Values {"DEF" "NONE"} -Min_Val 1.3 -Max_Val 3.5
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "PAREXP" -Instrument "ACS" -Cfg {"ACS/WFC" "ACS/HRC"}
    -Pure_Par_Allowed 1
    -Mode "ACCUM" -Type "string" -String_Values {"NONE"}
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "FOCUS" -Instrument "ACS" -Mode "ALIGN" -Type "numeric"
    -Pure_Par_Allowed 1
    -Min_Val -858 -Max_Val 858
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "TILT" -Instrument "ACS" -Mode "ALIGN" -Type "string"
    -Pure_Par_Allowed 1
    -String_Values {"NO" "YES"}
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "AUTOIMAGE" -Instrument "ACS" -Cfg {"ACS/WFC" "ACS/HRC"}
    -Mode "ACCUM" -Type "string"
    -Pure_Par_Allowed 1
    -String_Values {"YES" "NO"}}

Instrument_Optional_Parameter {-Name "CTE" -Instrument "ACS" -Cfg "ACS/WFC"
    -Pure_Par_Allowed 1
    -Mode "ACCUM" -Type "string"
    -String_Values {"NONE" "JCTWFS" "JCTWE"}
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "AMP" -Instrument "ACS" -Cfg {"ACS/WFC" "ACS/HRC"}
    -Pure_Par_Allowed 1
    -Mode "ACCUM" -Type "string"
    -String_Values {"A" "B" "C" "D" "AD" "BC" "ABCD"}
    -Availability "caut-use"}

Instrument_Optional_Parameter {-Name "CTE" -Instrument "ACS" -Cfg "ACS/HRC"
    -Pure_Par_Allowed 1
    -Mode "ACCUM" -Type "string"
    -String_Values {"NONE" "JCTHE" "JCTHFS" "JCTHFP"}
    -Availability "eng-only"}


#---- post-flash

# General observer FLASH requirement
Instrument_Optional_Parameter {-Name "FLASH" -Instrument "ACS"
    -Cfg "ACS/WFC" -Mode "ACCUM" -Type "numeric"
    -Pure_Par_Allowed 1
    -Min_Val 1 -Max_Val 5733 -Increment 1}
# Engineering FLASH requirements: FLASHCUR/FLASHEXP
Instrument_Optional_Parameter {-Name "FLASHCUR" -Instrument "ACS"
    -Cfg "ACS/WFC" -Mode "ACCUM" -Type "string"
    -Pure_Par_Allowed 1
    -String_Values {"LOW" "MEDIUM" "HIGH"}
    -Availability "eng-only"}
Instrument_Optional_Parameter {-Name "FLASHEXP" -Instrument "ACS"
    -Cfg "ACS/WFC" -Mode "ACCUM" -Type "numeric"
    -Min_Val 0.1 -Max_Val 409.5
    -Pure_Par_Allowed 1
    -Availability "eng-only"}

# FLASH cannot be specified with FLASHCUR or FLASHEXP
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASH"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHEXP"} {"*"}}}
    -Message "FLASH cannot be specified with FLASHEXP."}
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASH"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHCUR"} {"*"}}}
    -Message "FLASH cannot be specified with FLASHCUR."}

# FLASHCUR and FLASHEXP require one another
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASHCUR"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHEXP"} {! "*"}}}
    -Message "If FLASHCUR is specified, FLASHEXP must also be specified."}
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"}
	{{"optional_parameter" "FLASHEXP"} {"*"}}}
    -Result {{{"optional_parameter" "FLASHCUR"} {! "*"}}}
    -Message "If FLASHEXP is specified, FLASHCUR must also be specified."}

#---- (end of post-flash)

Instrument_Optional_Parameter {-Name "READTYPE" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/WFC"} -Mode "ACCUM" -Type "string"
    -String_Values {"DSINT" "CLAMP"}
    -Availability "eng-only"}

Instrument_Optional_Parameter {-Name "SPEED" -Instrument "ACS"
    -Pure_Par_Allowed 1
    -Cfg {"ACS/WFC"} -Mode "ACCUM" -Type "string"
    -String_Values {"FULL" "HALF"}
    -Availability "eng-only"}

#
# Legal cfg/mode combinations
#
Combination {-Type "legal" -Instrument "ACS" -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}}}
    -Result {{"mode" {"ACCUM" "ALIGN"}}}}
Combination {-Type "legal" -Instrument "ACS" -Condition {{"cfg" {"ACS/SBC"}}}
    -Result {{"mode" {"ACCUM"}}}}
Combination {-Type "legal" -Instrument "ACS" -Condition {{"cfg" {"ACS/HRC"}}}
    -Result {{"mode" {"ACQ"}}}}
Combination {-Type "legal" -Instrument "ACS" -Condition {{"cfg" {"ACS"}}}
    -Result {{"mode" {"ANNEAL"}}}}
#
# Legal/illegal spectral_element/aperture combinations
#
Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/WFC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-WFC-FILTERS" "DEF"}}}
    -Result {{"aperture" {"ACS-WFC" "ACS-WFC-SMALL" "ACS-WFC-IRAMP" "ACS-WFC-MRAMP" "ACS-WFC-ORAMP"}}}}

Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/WFC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-WFC-SMALL-FILTERS"}}}
    -Result {{"aperture" {"ACS-WFC-SMALL" "ACS-WFC-MRAMP"}}}}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/WFC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-WFC-SMALL-FILTERS"}}}
    -Result {{"aperture" {! "ACS-WFC-SMALL" "ACS-WFC-MRAMP"}}}}

Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/WFC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-IRAMP-FILTERS"}}}
    -Result {{"aperture" {"ACS-WFC-IRAMP"}}}}

Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/WFC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-MRAMP-FILTERS"}}}
    -Result {{"aperture" {"ACS-WFC-MRAMP"}}}}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/WFC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-MRAMP-FILTERS"}}}
    -Result {{"aperture" {! "ACS-WFC-MRAMP"}}}}

Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/WFC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-ORAMP-FILTERS"}}}
    -Result {{"aperture" {"ACS-WFC-ORAMP"}}}}

Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/HRC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-HRC-FILTERS" "DEF"}}}
    -Result {{"aperture" "ACS-HRC"}}}

Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/SBC"}} {"mode" {"ACCUM"}} {"spectral_element" {"ACS-SBC-FILTERS" "DEF"}}}
    -Result {{"aperture" "ACS-SBC"}}}

Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/HRC"}} {"mode" {"ACQ"}}}
    -Result {{"aperture" "ACS-HRC-ACQ"}}}
Combination {-Type "legal" -Instrument "ACS"
    -Condition {{"cfg" { "ACS/HRC"}} {"mode" {"ACCUM"}}}
    -Result {{"aperture" "ACS-HRC-CORON"}}}
#
# Legal cfg/spectral_element combinations, and mode/spectral_element combinations
#
Combination {-Type "legal" -Instrument "ACS" -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"}}
    -Result {{"spectral_element" {"ACS-WFC-FILTERS" "ACS-WFC-SMALL-FILTERS" "ACS-RAMP-FILTERS"}}}}

Combination {-Type "legal" -Instrument "ACS" -Condition {{"cfg" "ACS/HRC"} {"mode" {"ACCUM" "ACQ"}}}
    -Result {{"spectral_element" "ACS-HRC-FILTERS"}}}

Combination {-Type "legal" -Instrument "ACS" -Condition {{"cfg" "ACS/SBC"} {"mode" {"ACCUM"}}}
    -Result {{"spectral_element" "ACS-SBC-FILTERS"}}}
#
# Illegal cfg/calibration_target/mode combinations
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"mode" {! "ACCUM"}}}
    -Result {{"calibration_target" { "BIAS" "DARK" "TUNGSTEN" "DEUTERIUM"}}}
    -Message "Internal targets with ACS must use ACCUM mode." }

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {! "ACS/HRC" "ACS/SBC"}}}
    -Result {{"calibration_target" {"DEUTERIUM"}}}
    -Message "DEUTERIUM can only be used with the HRC or SBC." }

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {! "ACS/HRC" "ACS/WFC"}}}
    -Result {{"calibration_target" {"TUNGSTEN" "BIAS"}}}
    -Message "TUNGSTEN and BIAS can only be used with the HRC or WFC." }

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"mode" {! "ANNEAL" "ALIGN"}}}
    -Result {{"calibration_target" {"NONE"}}}
    -Message "NONE can only be used with ACS ANNEAL and ALIGN modes." }

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS" "ACS/HRC" "ACS/WFC"}} {"mode" {"ANNEAL" "ALIGN"}}}
    -Result {{"calibration_target" {! "NONE"}}}
    -Message "ACS ANNEAL and ALIGN modes must use target NONE." }

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"calibration_target" "BIAS"}}
    -Result {{"exp_time" {!= 0}}}
    -Message "ACS BIAS must be given an exposure time of zero"}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/HRC"} {"mode" "ACQ"}}
    -Result {{"exp_time" {> 300}}}
    -Availability "caut-use"
    -Message "ACS ACQ exposures must be less than 5 minutes in a GO proposal."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/SBC"}}
    -Result {{{"optional_parameter" {"GAIN" "CR-SPLIT" "SIZEAXIS2" "SIZEAXIS1"}}}}
    -Message "No optional parameters are allowed with the SBC."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"}}
    -Result {{{"optional_parameter" "GAIN"} {"0.5" "1.0" "1.4"}}}
    -Availability "caut-use"
    -Message "On ACS/WFC, this value for the GAIN optional parameter is unsupported."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/HRC"} {"mode" "ACCUM"}}
    -Result {{{"optional_parameter" "GAIN"} {"1" "8"}}}
    -Availability "caut-use"
    -Message "On ACS/HRC, the values of 1 and 8 for the GAIN optional parameter are unsupported."}

Combination {-Type "illegal" -Instrument "ACS"
   -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"}}
   -Result {{{"optional_parameter" "FLASHEXP"} {! "NONE" "SHORT" "MID" "LONG"}}}
   -Availability "eng-only"
   -Message "A numerical value for FLASHEXP is only permitted for engineering proposals."}

#
# Constraints added in support of OPR 42988
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"spectral_element" {"PR110L" "PR130L"}}}
    -Result {{"aperture" {! "SBC"}}}
    -Message "Aperture SBC must be specified if spectral element PR110L or PR130L is specified."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"spectral_element" {"PR200L"}}}
    -Result {{"aperture" {! "HRC"}}}
    -Message "Aperture HRC must be specified if spectral element PR200L is specified."}
#
# CTE may only be used with DARK, TUNGSTEN, targets
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"}
        {"optional_parameter" {"CTE"}}}
    -Result {{"calibration_target" {! "DARK" "TUNGSTEN"}}}
    -Message "CTE may only be used with DARK, TUNGSTEN, targets."}
#
# CTE may not be used with WFC subarray apertures.
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC"}} {"mode" "ACCUM"}
        {"optional_parameter" {"CTE"}}}
    -Result {{"aperture" {"WFC1-512" "WFC1-1K" "WFC1-2K" "WFC2-2K"}}}
    -Message "CTE may not be used with ACS/WFC subarray apertures WFC1-512, WFC1-1K, WFC1-2K or WFC2-2K."}
#
# If CTE is specified as JCTWFS or JCTWE, AMP must be AD or BC.
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC"}} {"mode" "ACCUM"}
        {{"optional_parameter" "CTE"} {"JCTWFS" "JCTWE"}}}
    -Result {{{"optional_parameter" "AMP"} {! "AD" "BC"}}}
    -Message "If CTE is specified as JCTWFS or JCTWE, AMP must be AD or BC."}
#
# CTE may not be used with HRC subarray apertures.
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/HRC"}} {"mode" "ACCUM"}
        {"optional_parameter" {"CTE"}}}
    -Result {{"aperture" {"HRC-512" "HRC-SUB1.8"}}}
    -Message "CTE may not be used with ACS/HRC subarray apertures HRC-512 or HRC-SUB1.8."}
#
# If CTE is specified as JCTHE, JCTHFS or JCTHFP" then AMP must be A, B, C or D
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/HRC"}} {"mode" "ACCUM"}
        {{"optional_parameter" "CTE"} {"JCTHE" "JCTHFS" "JCTHFP"}}}
    -Result {{{"optional_parameter" "AMP"} {! "A" "B" "C" "D"}}}
    -Message "If CTE is specified as JCTHE, JCTHFS or JCTHFP then AMP must be A, B, C or D."}

#
#AMP can only correspond to one detector with quadrant filters (PR 54532)
#
Combination {-Type "illegal" -Instrument "ACS"
-Condition {{"cfg" {"ACS/WFC"}} {"mode" "ACCUM"} {"aperture" "ACS-WFC1-QUADRANT"}}
    -Result {{{"optional_parameter" "AMP"} {! "A" "B"}}}
    -Message "When a quadrant aperture is specified, only the AMPs on the same WFC chip may be specified."}

Combination {-Type "illegal" -Instrument "ACS"
-Condition {{"cfg" {"ACS/WFC"}} {"mode" "ACCUM"} {"aperture" "ACS-WFC2-QUADRANT"}}
    -Result {{{"optional_parameter" "AMP"} {! "C" "D"}}}
    -Message "When a quadrant aperture is specified, only the AMPs on the same WFC chip may be specified."}

# Constraint added in support of OPR 43995
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/SBC"}}}
    -Result {{"calibration_target" {"EARTH-CALIB"  "DARK-EARTH-CALIB"}}}
    -Message "EARTH-CALIB and DARK-EARTH-CALIB are not allowed with the ACS/SBC configuration."}
#
# Constraint added in support of OPR 44341
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"} {{"optional_parameter" "SIZEAXIS1"} {"*"}}}
    -Result {{"spectral_element" "ACS-WFC-SMALL-FILTERS"}}
    -Message "SIZEAXIS1 may not be specified if the Spectral Element specification
            includes F892N or a polarizer."
    -Explanation "When F892N or a polarizer is specified, STScI will automatically
            assign a subarray containing the entire FOV provided by those spectral elements.
            The subarray is approximately one quarter the size of the full WFC array.
            those subarray parameters may not be overridden."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"} {{"optional_parameter" "SIZEAXIS2"} {"*"}}}
    -Result {{"spectral_element" "ACS-WFC-SMALL-FILTERS"}}
    -Message "SIZEAXIS2 may not be specified if the Spectral Element specification
            includes F892N or a polarizer."
    -Explanation "When F892N or a polarizer is specified, STScI will automatically
            assign a subarray containing the entire FOV provided by those spectral elements.
            The subarray is approximately one quarter the size of the full WFC array.
            those subarray parameters may not be overridden."}
            
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"} {{"optional_parameter" "CENTERAXIS1"} {"*"}}}
    -Result {{"spectral_element" "ACS-WFC-SMALL-FILTERS"}}
    -Message "CENTERAXIS1 may not be specified if the Spectral Element specification
            includes F892N or a polarizer."
    -Explanation "When F892N or a polarizer is specified, STScI will automatically
            assign a subarray containing the entire FOV provided by those spectral elements.
            The subarray is approximately one quarter the size of the full WFC array.
            those subarray parameters may not be overridden."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"} {{"optional_parameter" "CENTERAXIS2"} {"*"}}}
    -Result {{"spectral_element" "ACS-WFC-SMALL-FILTERS"}}
    -Message "CENTERAXIS2 may not be specified if the Spectral Element specification
            includes F892N or a polarizer."
    -Explanation "When F892N or a polarizer is specified, STScI will automatically
            assign a subarray containing the entire FOV provided by those spectral elements.
            The subarray is approximately one quarter the size of the full WFC array.
            those subarray parameters may not be overridden."}            
#
# CTE may not be JCTWFS or JCTWE with Spectral Element F892N or Polarizer
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"} {{"optional_parameter" "CTE"} {"JCTWFS" "JCTWE"}}}
    -Result {{"spectral_element" "ACS-WFC-SMALL-FILTERS"}}
    -Message "CTE may not be specified as JCTWFS or JCTWE if the Spectral Element specification
            includes F892N or a polarizer."
    -Explanation "When F892N or a polarizer is specified, STScI will automatically
            assign a subarray containing the entire FOV provided by those spectral elements.
            The subarray is approximately one quarter the size of the full WFC array.
            those subarray parameters may not be overridden."}

# SIZEAXIS[1-2] cannot be used on Subarray Aperture

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} {{"optional_parameter" "SIZEAXIS1"} {"*"}}}
    -Result {{"aperture" {"ACS-SUBARRAY"}}}
    -Message "SIZEAXIS1 may not be specified if the Aperture is a Subarray Aperture."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} {{"optional_parameter" "SIZEAXIS2"} {"*"}}}
    -Result {{"aperture" {"ACS-SUBARRAY"}}}
    -Message "SIZEAXIS2 may not be specified if the Aperture is a Subarray Aperture."}

#
# CENTERAXIS[1-2] can only be used in conjunction with SIZEAXIS[1-2]
# and SIZEAXIS[1-2] must be a numeric value
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" {"ACCUM"}} {{"optional_parameter" "CENTERAXIS1"} {"*"}}}
    -Result {{{"optional_parameter" "SIZEAXIS1"} {! "*"}}}
    -Message "CENTERAXIS1 may only be specified if SIZEAXIS1 is specifed." }

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" {"ACCUM"}} {{"optional_parameter" "CENTERAXIS2"} {"*"}}}
    -Result {{{"optional_parameter" "SIZEAXIS2"} {! "*"}}}
    -Message "CENTERAXIS2 may only be specified if SIZEAXIS2 is specifed." }

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" "ACS/WFC"} {"mode" "ACCUM"} {{"optional_parameter" "CENTERAXIS2"} {> 2039}}}
    -Result {{{"optional_parameter" "CENTERAXIS2"} {< 2057}}}
    -Message "CENTERAXIS2 should be between 9 and 2039 inclusive or between 2057 and 4087 inclusive or TARGET."}
#
# CR-SPLIT may not be specfied on internal targets
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} {{"optional_parameter" "CR-SPLIT"} {"*"}}}
    -Result {{"calibration_target" {"BIAS" "DARK" "TUNGSTEN" "DEUTERIUM"}}}
    -Message "CR-SPLIT may not be specified on Internal Targets.  All internal target exposures will be taken as a single exposure with an implicit CR-SPLIT = NO" }
#
# AUTOIMAGE may not be specified on internal targets
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} {{"optional_parameter" "AUTOIMAGE"} {"*"}}}
    -Result {{"calibration_target" {"BIAS" "DARK" "TUNGSTEN" "DEUTERIUM"}}}
    -Message "AUTOIMAGE may not be specified on Internal Targets." }

#
# FLASH, FLASHEXP and FLASHCUR may not be specified on internal target BIAS
#

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} 
	{{"optional_parameter" {"FLASHCUR" "FLASHEXP" "FLASH"}} "*"}}
    -Result {{"calibration_target" {"BIAS"}}}
    -Message "FLASH, FLASHEXP and FLASHCUR may not be specified on Internal Target BIAS." }

#
# AUTOIMAGE may not be specified on internal target BIAS
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} {{"optional_parameter" "AUTOIMAGE"} {"*"}}}
    -Result {{"calibration_target" {"BIAS"}}}
    -Message "AUTOIMAGE may not be specified on Internal Target BIAS." }

#
# PAREXP may not be specified on internal target BIAS TUNGSTEN DEUTERIUM
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} {{"optional_parameter" "PAREXP"} {"*"}}}
    -Result {{"calibration_target" {"BIAS" "TUNGSTEN" "DEUTERIUM"}}}
    -Message "PAREXP may not be specified on Internal Targets BIAS, TUNGSTEN, or DEUTERIUM." }
#
# CTE may not be specified on internal targets BIAS and DEUTERIUM
#
Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"mode" "ACCUM"} {{"optional_parameter" "CTE"} {"*"}}}
    -Result {{"calibration_target" {"BIAS" "DEUTERIUM"}}}
    -Message "CTE may not be specified on Internal Targets BIAS or DEUTERIUM." }

#
Combination {-Type "legal" -Instrument "ACS"
-Condition {{"cfg" {"ACS/WFC" "ACS/HRC"}} {"calibration_target" {"DARK" "BIAS"}}}
-Result {{"spectral_element" "DEF"}}
-Message "DEF is only allowed when ACS/WFC, ACS/HRC in ACCUM mode and calibration target is DARK or BIAS"}

Combination {-Type "legal" -Instrument "ACS"
-Condition {{"cfg" "ACS/SBC"} {"calibration_target" {"DARK"}}}
-Result {{"spectral_element" "DEF"}}
-Message "DEF is only allowed when ACS/SBC, in ACCUM mode and calibration target is DARK"}

Combination {-Type "illegal" -Instrument "ACS"
-Condition {{"cfg" {"ACS/WFC" "ACS/HRC" "ACS/SBC"}} {"spectral_element" "DEF"}}
-Result {{mode {! "ACCUM"}}}
-Message "DEF is only allowed when ACS/WFC, ACS/HRC in ACCUM mode and calibration target is DARK or BIAS"}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/HRC" "ACS/WFC"}} {"spectral_element" {"ACS-FILTERS-1" "ACS-CLEARS-1"}}}
    -Result {{"spectral_element" "ACS-POLARIZERS-1"}}
    -Message "A filter must be crossed with a polarizer on the other wheel."}

Combination {-Type "illegal" -Instrument "ACS"
    -Condition {{"cfg" {"ACS/HRC" "ACS/WFC"}} {"spectral_element" {"ACS-FILTERS-2" "ACS-CLEARS-2"}}}
    -Result {{"spectral_element" "ACS-POLARIZERS-2"}}
    -Message "A filter must be crossed with a polarizer on the other wheel."}

Combination {-Type "illegal" -Instrument "ACS"
   -Condition {{"cfg" {"ACS"}}}
   -Result {{"calibration_target" {! "NONE"}}}
   -Message "Only target NONE is allowed with config ACS."}   

}

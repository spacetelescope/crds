Calculating Time
----------------

The Exposure Time is calculated based on the user input SNR, instrument
configuration and input source spectrum. For spectroscopic modes, this value is
calculated at a particular wavelength which is specified by the user in Section
2 of the ETC forms. 

**Please  make sure the wavelength entered in this section is covered by the selected mode.**

With this information, the count rate terms (in photons/sec) are retrieved from
*pysynphot*. Each photon count rate term is depicted below with an :sub:`r` subscript.

Taking formula (ii) from the previous page and expanding the count terms, we
get the following:


.. SNR = (S_r * t) / (sqrt(S_r * t  + Sky_r * t  + DC_r * t  + RN^2  + Thermal_r * t +  CS_r * t))

|          :math:`\text{\sl SNR} = \frac{S_{r}t}{\sqrt{S_{r}t + Sky_{r}t + \text{\sl DC}_{r}t + RN^{2} + (Thermal_{r}t) + (\text{\sl CS}_{r}t)}}`

This can be easily changed to:

.. S_r^2  *  t^2  -  SNR^2 * [ S_r + Sky_r + DC_r + Thermal_r + CS_r] * t  - SNR^2 * RN^2  = 0

|          :math:`S_{r}^2 \cdot t^{2} - \text{\sl SNR}^{2} \cdot [ S_r + Sky_r + \text{\sl DC}_r + (Thermal_r) + (\text{\sl CS}_r) ] \cdot t - \text{\sl SNR}^{2} \cdot \text{\sl RN}^{2} = 0` 

Then solving for t gives us:

.. t = (b + sqrt(b^2 + 4ac)) / 2a

|          :math:`t = \frac{b + \sqrt{b^2 + 4ac}}{2a}`

*Where*:

.. a = S_r ^ 2
.. b = (S_r + BG_r) * SNR^2
.. c = RN^2 * SNR^2
.. BG_r = ES_r + ZL_r + GL_r + DC_r + Thermal_r + CS_r

|     :math:`a = S_{r}^{2}`
|     :math:`b = (S_{r} + \text{\sl BG}_{r}) \cdot \text{\sl SNR}^{2}`
|     :math:`c = \text{\sl RN}^{2} \cdot \text{\sl SNR}^{2}`
|     :math:`\text{\sl BG}_{r} =  \text{\sl ES}_{r} + \text{\sl ZL}_{r} + \text{\sl GL}_{r} + \text{\sl DC}_{r} + Thermal_{r} + \text{\sl CS}_{r}`
|  
|     :math:`S_{r}` = *Source count rate*
|     :math:`\text{\sl SNR}` = *Signal To Noise ratio*
|     :math:`\text{\sl ES}_{r}` = *Earthshine count rate*
|     :math:`\text{\sl ZL}_{r}` = *Zodiacal Light count rate*
|     :math:`\text{\sl GL}_{r}` = *Geocoronal Emission Line(s) count rate*
|     :math:`\text{\sl DC}_{r}` = *Dark Current count rate*
|     :math:`Thermal_{r}` = *Thermal background count rate (optional field)*
|     :math:`\text{\sl CS}_{r}` = *Coronagraphic Source count rate (optional field)*
|     :math:`\text{\sl RN}` = *Read Noise*


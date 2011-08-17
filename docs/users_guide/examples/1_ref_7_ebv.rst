.. _ebv-and-interstellar-extinction:

E(B-V) and the Interstellar Extinction Curves
---------------------------------------------

The ETC supports six different extinction relations:

- **Milky Way Diffuse:** An average Galactic extinction curve for diffuse ISM (Rv=3.1) taken from Cardelli, Clayton, & Mathis [CCM]_ 

- **Milky Way Dense:** A Galactic extinction curve for dense/molecular ISM (Rv=5.0), also taken from Cardelli, Clayton, & Mathis [CCM]_ 

- **LMC Average:** Large Magellanic Cloud extinction (Rv=3.41) away from 30Dor, taken from [Gordon]_ et al

- **LMC 30DorShell:** Large Magellanic Cloud extinction for the Supershell/30Dor region (Rv=2.76), also taken from [Gordon]_ et al 

- **SMC Bar:** Small Magellanic Cloud extinction (Rv=2.74), also taken from [Gordon]_ et al

- **Starburst (attenuation law):** A general extra-galactic extinction curve appropriate for stellar continuum, taken from [Calzetti]_ et al


Normally, the extinction factor is applied by default before the flux
is normalized to the specified value in Sec.4. That is, in this case
the normalized flux will correspond to the actual observed flux.

One can, however, specify an alternate computation order, in which the
extinction is applied **after** the normalization takes place. This is
useful when planning observations of targets where the "observed
magnitude" is being calculated from the absolute magnitude and
distance for a region of space in which there is a known, measured
extinction.




.. [CCM] Cardelli, Clayton & Mathis (ApJ, 345, 245, 1989)

.. [Gordon] Gordon et al. (2003, ApJ, 594, 279)

.. [Calzetti] Calzetti et al. (2000. ApJ, 533, 682)


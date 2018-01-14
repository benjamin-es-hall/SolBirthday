\begintext
    Benjamin E. S. Hall
    Created Jan 2017

    Contains base SPICE kernels useful for basic SPICE functions such as
    identifying body codes and calculating main solar system body ephmeris.
    Spacecraft ephemeris will NOT be possible as their kernels are bespoke.
    That is, each spacecraft tends to have their own naming scheme for SCLK,
    FK, CK, and SPK. Thus, their is no easy way to `generalise` all spaceraft
    kernels.

    File name                     Contents
    ---------                     --------
    naif0012.tls                  Leapseconds kernel

    pck00010.tpc                  Planet orientation and radii

    RSSDVvvv.TF                   Provides mission independent reference
								  frame definitions suitable for a number of ESA
                                  and NASA missions. Includes: HEE, HEEQ, GSE,
                                  MSO etc. See file for included frames

    *de431_1850_2100.bsp.bsp      Generic kernel for determining planetary
                                  state (position + velocity)
                                  * NOTE: This has been custom created using
								  		  NASA SPICE spkmerge tools on
										  de431_part-2.bsp. This covers date
										  range 1850-01-01 to 2100-01-01

\begindata

    PATH_VALUES       = ('./assets/spice/')

    PATH_SYMBOLS      = ( 'KERNELS' )

    KERNELS_TO_LOAD = (
                        '$KERNELS/lsk/NAIF0012.TLS'

                        '$KERNELS/pck/pck00010.tpc'

                        '$KERNELS/fk/RSSD0002.TF'

                        '$KERNELS/spk/de431_1850_2100.bsp'

                      )

\begintext

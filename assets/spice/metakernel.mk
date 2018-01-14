\begintext
    Benjamin E. S. Hall
    Created 10 Aug 2017

    Contains base SPICE kernels useful for basic SPICE functions such as
    identifying body codes and calculating main solar system body ephmeris.
    Spacecraft ephemeris will NOT be possible as their kernels are bespoke.
    That is, each spacecraft tends to have their own naming scheme for SCLK,
    FK, CK, and SPK. Thus, their is no easy way to `generalise` all spaceraft
    kernels.

    The lores merely describes the EARTH frame kernels used. Please use hires
    if high-accuracy, short term ephemeris are required local to Earth.

    Includes the effects of Earth's precession, nutation (and correction),
    rotation through true siderial time, and polar motion matter, we suggest
    using the hires metakernel.

    File name                     Contents
    ---------                     --------
    naif0012.tls                  Leapseconds kernel

    gm_de431.tpc                  "GM" (grav constant times mass) values for
                                  the sun, planets, planetary system
                                  barycenters, and selected satellite asteroids

    pck00010.tpc                  Planet orientation and radii

    EARTHFIXEDIAU.TF              Provides frame alias between EARTH_FIXED
                                  and IAU_EARTH. Appropriate for long-term
                                  ephemeris predictions local to Earth

    EARTH_TOPO_YYMMDD.TF          Provides topocentric reference frame
                                  definitions associated with the
                                  Earth based Deep Space Network (DSN) stations

    ESTRACK_Vvv.TF                Provides topocentric reference frame
                                  definitions for ESA tracking ground stations

    NEW_NORCIA_TOPO.TF            Provides topocentric reference frame
                                  definition for European Space Agency (ESA)
                                  35m tracking antenna in New Norcia

    RSSDVvvv.TF                   Provides mission independent reference frame
                                  definitions suitable for a number of ESA
                                  and NASA missions. Includes: HEE, HEEQ, GSE,
                                  MSO etc. See file for included frames

    *de430s.bsp                   Generic kernel for determining planetary
                                  state (position + velocity)
                                  * NOTE: NO LONGER INCLUDES STATE OF MARS'
                                          MASS CENTRE (NAID IF 499).
                                          MARS' SYSTEM BARYCENTER (NAIF ID 4)
                                          IS INCLUDED. OFFSET BETWEEN 499 AND
                                          4 EQUATES TO ABOUT 20 cm.
                                          SPK MAR097.BSP HAS BEEN INCLUDED TO
                                          ADD 499 BACK (also includes Mars'
                                          natural satellites)

    *MAR097.BSP                  Provides state vectors for Mars' system
                                 barycenter (NAIF ID 499) and its natural
                                 satellites
                                 * NOTE: THIS IS INCLUDED SINCE DE430.BSP
                                         NO LONGER INCLUDES 499. HOWEVER, THIS
                                         SPK IS A LARGE FILE, AND IF
                                         PORTABILITY MATTERS AND THE 20cm
                                         DIFFERENCE (see above) DOESN'T MATTER
                                         PLEASE REMOVE IT FROM HERE AND YOUR
                                         PORTABLE KERNEL COPY

    EARTHSTNS_FX_YYMMDD.BSP     Provides state vectors (geocentric) for Earth
                                based DSN stations. Uses alias frame mapping
                                described in EARTHFIXEDIAU.TF. Date corresponds
                                to file creation and this is suitable for
                                long-term state predictions

    ESTRACK_V01.BSP             Provides draft state vectors (geocentric) for
                                ESA tracking stations.

    NEW_NORCIA.BSP              Provides state vectors (geocentric) for ESA
                                35m tacking station in New Norcia.


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

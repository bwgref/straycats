# StrayCats


## The current version of the FITS table can be found [here](https://github.com/bwgref/straycats/blob/master/straycats.fits)

## An interactive version of the table can be found [here](./tables/straycat_table)


### The columns are:

1. Classifictation

    As of now, either SL (for confirmed stray light source) or ??. In the future also include GR (for Ghost Rays from source just outside of the FoV), Faint, etc.
  
2. SL Target

    The name of the SL target.

3. SEQID

    The sequence ID for the NuSTAR observation where SL was observed. If a SL Target is observed in multiple sequence IDs then there are multiple rows in the table for that sequence ID.

4. Module

    The module in which SL was observed. Either A or B. If both A and B then there are multiple rows for that sequence ID.

5. Exposure (s)

    The exposure time in seconds for that observation

6. RA / Dec

    The RA / Dec for the *targeted* observation (i.e., not the SL Target)

7. TIME / END_TIME

    The MJD start / end time of the observation

8. Notes

    Any notes for the SL observation (probably to be removed at some point).

### Update plan

The Google docs will remain the underlying source of the information. So as we identify more of the unidentified SL sources we'll update those tables, dump them to CSV files, and then regenrated the FITS version of the catalog.


## Sky distribution of SL sources

<iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="https://bwgref.github.io/straycats/plotly_figs/straycat_radec.html" height="525" width="100%"></iframe>

## Galactic distribution of SL sources. Underlying image is the [ESO Milky Way panorama](https://www.eso.org/public/images/eso0932a/)
### Use the 'Zoom' tool to manipulate this image rather than the "Box Select" tool.
<iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="https://bwgref.github.io/straycats/plotly_figs/galaxy_overlay.html" height="525" width="100%"></iframe>



<iframe id="igraph" scrolling="yes" seamless="seamless" src="https://bwgref.github.io/straycats/tables/straycats_table.html" height="525" width="100%"></iframe>
 

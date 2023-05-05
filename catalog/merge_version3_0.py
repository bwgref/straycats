from astropy.table import Table



# Read the last version and append the new one
from astropy.table import vstack
 
v1 = Table.read('fits/straycats_v2_1.fits', format = 'fits')
v2_incr = Table.read('fits/straycats_incr3_0.fits', format = 'fits')
v2 = vstack([v1, v2_incr])
v2.write('fits/straycats_v3_0.fits', overwrite=True)




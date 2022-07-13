from astropy.table import Table
import numpy as np
import urllib
from astropy.time import Time
import os
from glob import glob
import shutil

seqid_base = 'https://github.com/NuSTARStrayCats/straycats/tree/master/web_resources/seqid'

sf = '../../../straycats.fits'
straycat = Table.read(sf)
for key in straycat.columns:
    if straycat[key].dtype.str.startswith('|S'):
        straycat[key] = straycat[key].astype('str') 
df = straycat.to_pandas()
df.columns

# Strip out unknowns:
sl = df[(df['Classification']=='SL') & (df['RA_SL'] > 0)].copy().reset_index(drop=True)
sl = sl.drop(['END_TIME', 'Multi'], axis=1)

# Reformat as necessary

sl['Exposure'] = sl['Exposure'] / 1e3
sl['Exposure (ks)'] = sl['Exposure'].map('{:.2f}'.format)
sl['MJD'] = sl['TIME'].map('{:.1f}'.format)
sl['Area (cm2)'] = sl['Area (cm2)'].map('{:.1f}'.format)
sl['Date'] = [Time(x, format = 'mjd').iso for x in sl['TIME']]

sl['Region'] = sl['SEQID'].astype(str)+sl['Module']+'_'+sl['STRAYID']


for key in ['HR', 'Error HR', '3-8 keV count/s/cm2', 'Error 3-8 keV count/s/cm2',
       '8-13 keV count/s/cm2', 'Error 8-13 keV count/s/cm2',
       '3-8 keV bkgd count/s/cm2', 'Error 3-8 keV bkgd count/s/cm2',
       '8-13 keV bkgd count/s/cm2', 'Error 8-13 keV bkgd count/s/cm2']:
    sl[key] = sl[key].map('{:.3f}'.format)


# Get unique number of seqid rows:

uniq_sl = sl.copy()
uniq_sl['Number of Obs'] = ""

nobs = uniq_sl['SL Source'].value_counts()

summary_redlist = ['SL Source', 'SL Type', 'RA_SL', 'DEC_SL', 'Number of Obs']
summary_greenlist = ['MJD', 'Date', 'Module',
                    'Classification', 'Primary', 
                    'SEQID','Exposure (ks)', 'Area (cm2)',
                    '3-8 keV count/s/cm2', '8-13 keV count/s/cm2', 'HR', 'Region']


for source in np.unique(uniq_sl['SL Source']):

    this_src = uniq_sl[uniq_sl['SL Source'] == source].copy().reset_index(drop=True)
    
    sname = source.replace(" ", "")
    
#     if sname != 'SMCX-1':
#         continue
    print(sname)
    this_summary = f'{sname}_summary.html'

    
    this_src = this_src[summary_greenlist]
    this_src = this_src.sort_values('MJD', axis = 0)
    
    if not os.path.isdir(sname):
        print(os.path.isdir)
        os.mkdir(sname)

    this_summary = os.path.join(sname, this_summary)
    
    
    
    for index, row in this_src.iterrows():
        seqid=row['SEQID']
        mod = row['Module']
        
        indir = os.path.join('./sl_products/', f'{seqid}')
        if not os.path.isdir(indir):
            print(f'Missing products: {seqid}')
            continue
        seq_html = os.path.join(sname, f'{sname}_{seqid}{mod}.html')
        
        for file in glob(f'{indir}/*'):
#            print(file)
            shutil.copy(file, sname)
        
        with open(seq_html, 'w') as f:
            f.write('<header>')
            f.write(f'<h1> {source} {seqid} {mod}</h1>\n')
            f.write('</header>\n')
            f.write('<body>\n')
            f.write('<center>\n')


            im_file = f'nu{seqid}{mod}01_cl_im.pdf'
            if not os.path.exists(f'{sname}/{im_file}'):
                print(f'Missing {im_file}')
            else:
                f.write(f'<embed src={im_file} width="600pix" height="460pix" class="center"/>\n')
    #        f.write(f'<img src={lc_file}  width="100%" height="460pix" class="center"/>\n')

            f.write('<p>\n')
            f.write('Smoothed DET1 3--20 keV DET1 image with extraction region.')
            f.write('</p>\n')
            
            spec_file = f"nu{seqid}{mod}01_cl_{row['Region']}_sr.pdf"
                
            f.write('</center>\n')

            f.write('<center>\n')
            if not os.path.exists(f'{sname}/{spec_file}'):
                print(f'Missing {spec_file}')
            else:
                f.write(f'<embed src={spec_file} width="600pix" height="460pix" class="center"/>\n')
            f.write('<p>\n')
            f.write('Source Spectrum, no background subtraction.')
            f.write('</p>\n') 
            f.write('</center>')

            for t in [1000, 100, 10]:            
                lc_file = f"{sname}/nu{seqid}{mod}01_{row['Region']}_3to20_{t}s_sr.pdf"
                if not os.path.exists(lc_file):
                    print(f'Missing {t} {lc_file}')
                else:
    #                print(lc_file)
                    f.write('<center>\n')
                    f.write(f'<embed src={os.path.basename(lc_file)} width="600pix" height="460pix" class="center"/>\n')
                    f.write('<p>\n')
                    f.write(f'Lightcurve at {t}s resolution\n')
                    f.write('</p>\n') 
                    f.write('</center>')


    
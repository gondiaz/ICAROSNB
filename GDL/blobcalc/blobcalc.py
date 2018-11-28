import os
import sys
import argparse

import csth.utils.pmaps_functions           as pmapsf
import csth.utils.hpeak_pmaps_newfunctions  as hppmap

import krcal.dev.corrections                as corrections

from invisible_cities.database.load_db import DataSiPM

import csth.images.voxelization as vx
import csth.images.blob         as b

import numpy                as np
import pandas               as pd
import matplotlib.pyplot    as plt

from scipy                   import optimize
from scipy.integrate         import quad


parser = argparse.ArgumentParser()
parser.add_argument("-r"  , "--run-number"     , type=int , help="run number")
parser.add_argument("-ty" , "--type"           , type=str , help="type of event (e.g. Cs, Tlds, Tlpk ...)")
parser.add_argument("-cd" , "--corrections-dir", type=str , help="corrected events summary directory")
parser.add_argument("-pd" , "--pmaps-dir"      , type=str , help="pmaps directory")
parser.add_argument("-El" , "--Elim"           , type =int, help="Energy limits in pk"  , nargs=2)
parser.add_argument("-rf" , "--rfactor"        , type =int, help="sipm reduction factor", nargs=2)
parser.add_argument("-zd" , "--zreb"           , type =int, help="slice distance")
parser.add_argument("-R"  , "--blob-radius"    , type =int, help="blob radius")
parser.add_argument("-tg"  , "--tag"           , type =str, help="tag for blobdf")

args = parser.parse_args(sys.argv[1:])

run              = args.run_number
typo             = args.type
evtcorrec_dir    = args.corrections_dir
pmaps_dir        = args.pmaps_dir
Ea, Eb           = args.Elim
rx, ry           = args.rfactor
zd               = args.zreb
R                = args.blob_radius
tag              = args.tag

datasipm = DataSiPM(run)
xpos, ypos = datasipm.X.values, datasipm.Y.values
correction_filename = f"$IC_DATA/maps/kr_corrections_run{run}.h5"
correction_filename = os.path.expandvars(correction_filename)
calibrate = corrections.Calibration(correction_filename, 'scale')

# EVENT SELECTION
typo='Tlds'
df = pd.HDFStore(f'{evtcorrec_dir}/corrections_6206_{typo}.h5')['/edf']
ipk = 0
evtsdf = df[(df.e<Eb) & (df.e>Ea) & (df.peak==ipk)][['event', 'peak', 'loc']]

#BLOB CALCULUS
# LOOP IN EVENTS
blobsdf = pd.DataFrame(columns=['event', 'peak', 'E1', 'E2', 'E3'])
j=1
for ev, ipk, loc in zip(evtsdf['event'], evtsdf['peak'], evtsdf['loc']):
    datadir  = f'{pmaps_dir}/pmaps_{loc}_{run}_{typo}.h5'
    data     = pd.HDFStore(datadir)

    s1   , s2   , s2si    = data['s1']      , data['s2']      , data['s2si']

    s1_ev = s1[(s1.event==ev)&(s1.peak==ipk)]
    s2_ev, s2si_ev = s2[(s2.event==ev)&(s2.peak==ipk)], s2si[(s2si.event==ev)&(s2si.peak==ipk)]

    pmap=(s1_ev, s2_ev, s2si_ev)
    x0ij, y0ij, z0ij, eij, _ = hppmap.get_event_hits(pmap, calibrate, xpos, ypos)

    imagedf = pd.DataFrame(columns=['X', 'Y', 'Z', 'E'])
    imagedf['X'], imagedf['Y'], imagedf['Z'], imagedf['E'] = x0ij, y0ij, z0ij, eij

    # EVENT VOXELIZATION
    imdf = vx.imageDataFrame(imagedf, datasipm, rx, ry, zd, th=0)

    #EVENT BLOB CALC
    Eb=[]
    i=0
    while i<3:
        blobdf, imdf_nb = b.blob(imdf, R)
        Eb.append(blobdf['E'].sum())
        imdf = imdf_nb
        i+=1

    blobsdf = blobsdf.append({'event':ev, 'peak':ipk, 'E1':Eb[0], 'E2':Eb[1], 'E3':Eb[2]}, ignore_index=True)

    print(f'Events saved:{j}/{len(evtsdf)}', end = '\r')
    j+=1

if zd<0: filename=f'./DATA/blobsdf_{tag}_{run}_{typo}_{R}_{rx}_{ry}_no.h5'
else   : filename=f'./DATA/blobsdf_{tag}_{run}_{typo}_{R}_{rx}_{ry}_{zd}.h5'
blobsdf.to_hdf(filename, key = 'blobs')

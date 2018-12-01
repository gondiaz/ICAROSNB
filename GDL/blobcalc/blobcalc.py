import os
import sys
import argparse

import numpy                as np
import pandas               as pd

from invisible_cities.database.load_db import DataSiPM

import csth.utils.cepeak_pmaps  as cpkpmap
import csth.utils.pmaps         as pmapdf
import csth.utils.cepeak        as cpk
import csth.images.voxelization as vx
import csth.images.blob         as bl



parser = argparse.ArgumentParser()
parser.add_argument("-r"  , "--run-number"     , type=int , help="run number")
parser.add_argument("-cf" , "--evtsum-filename", type=str , help="corrected events summary directory")
parser.add_argument("-pd" , "--pmaps-dir"      , type=str , help="pmaps directory")
parser.add_argument("-tg"  , "--tag"           , type =str, help="tag for pmaps")
parser.add_argument("-kr" , "--krmap-dir"      , type=str , help="kr maps directory")

parser.add_argument("-El" , "--Elim"           , type =int, help="Energy limits in pk"  , nargs=2)
parser.add_argument("-rf" , "--rfactor"        , type =int, help="sipm reduction factor", nargs=2, default=[1, 1])
parser.add_argument("-zd" , "--zreb"           , type =int, help="slice distance"                , default=-1)
parser.add_argument("-R"  , "--blob-radius"    , type =int, help="blob radius")

parser.add_argument("-od"  , "--out-dir"       , type =str, help="output directory")


args = parser.parse_args(sys.argv[1:])


run              = args.run_number
evtsum_filename  = args.evtsum_filename
pmaps_dir        = args.pmaps_dir
tag              = args.tag
krmap_dir        = args.krmap_dir

a, b             = args.Elim
rx, ry           = args.rfactor
zd               = args.zreb
R                = args.blob_radius

out_dir          =args.out_dir


def cepeak(run_number, input_filename, correction_filename, evt, pk, q0min):
    pmaps, runinfo        = cpkpmap.data(input_filename)
    calibrate, xpos, ypos = cpkpmap.tools(correction_filename, run_number)
    pmap  = pmapdf.get_eventpeak(pmaps, evt, pk)
    epk   = cpkpmap.epeak(pmap, xpos, ypos, q0min)
    if (epk is None):
        print('No epeak!!')
    cepk  = cpk.cepeak(epk, calibrate)
    return epk, cepk


# EVENT SELECTION
data = pd.HDFStore(evtsum_filename)['/esum']
datasipm = DataSiPM(run)

#correctiondir
correction_filename = f'{krmap_dir}/kr_corrections_run{run}.h5'

#photopeak region for run
thds = data[(a<data['e'])&(data['e']<b)]
evts, pks, locs = thds['event'].values, thds['peak'].values, thds['location'].values

blobsdf = pd.DataFrame(columns=['event', 'peak', 'loc', 'E1', 'E2', 'E3'])
#BLOB CALCULUS
# LOOP IN EVENTS
j=1
# LOOP IN EVENTS
for evt, pk, loc in zip(evts, pks, locs):
    loc = '{:04}'.format(loc)

    print(evt, pk, loc)

    #input and correction files
    input_filename = f'{pmaps_dir}/pmaps_{loc}_{run}_{tag}.h5'

    #imagedf
    _, cepk = cepeak(run, input_filename, correction_filename, evt, pk, q0min=6)
    xij, yij, zij, eij = cepk.xij, cepk.yij, cepk.zij, cepk.eij
    imagedf = pd.DataFrame(columns=['X', 'Y', 'Z', 'E'])
    imagedf['X'], imagedf['Y'], imagedf['Z'], imagedf['E'] = xij, yij, zij, eij

    #voxelized imagedf
    #imdf = vx.imageDataFrame(imagedf, datasipm, rx, ry, zd, th=0)
    imdf = imagedf

    #EVENT BLOB CALC
    Eb=[]
    i=0
    while i<3:
        blobdf, imdf_nb = bl.blob(imdf, R)
        Eb.append(blobdf['E'].sum())
        imdf = imdf_nb
        i+=1

    blobsdf = blobsdf.append({'event':evt, 'peak':pk, 'loc':loc, 'E1':Eb[0], 'E2':Eb[1], 'E3':Eb[2]}, ignore_index=True)

    print(f'Events saved:{j}/{len(thds)}', end = '\r')
    j+=1

filename=f'{out_dir}/blobs3_{run}_{a}_{b}_radious{R}.h5'
blobsdf.to_hdf(filename, key = 'blobs')

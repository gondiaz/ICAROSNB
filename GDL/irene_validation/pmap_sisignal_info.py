import glob
import numpy             as np
import pandas            as pd

from invisible_cities.io.pmaps_io import load_pmaps_as_df

to_df = pd.DataFrame.from_records


import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i" , "--indir" , type=str, help="pmapdir")
parser.add_argument("-n" , "--nfiles", type=int, help="npmaps")
parser.add_argument("-o"  , "--out"  , type=str, help="outdir")

args = parser.parse_args(sys.argv[1:])

pmapdir     = args.indir
npmaps      = args.nfiles
outfilename = args.out


def Pmaps_SiSignal_info(pmapdir, npmaps, outfilename):

    Q, n_si = [], []
    Q_per_slide = []

    evts = []

    FILES = glob.glob(pmapdir + "/*")
    FILES.sort()
    FILES = FILES[:npmaps]

    for pmap in FILES:

        _, S2pmap, S2Sipmap, _, _ = load_pmaps_as_df(pmap)

        EVENTS = np.unique(S2pmap["event"].values)

        #loop in events
        for ev in EVENTS:
            S2   = S2pmap  [S2pmap  ["event"]==ev]
            S2Si = S2Sipmap[S2Sipmap["event"]==ev]

            #loop in peaks
            PEAKS = np.unique(S2["peak"])
            for pk in PEAKS:
                S2Si_pk = S2Si [ S2Si["peak"] == pk ]

                #total change and number of sipms
                Q   .append(        np.sum(S2Si_pk["ene"]) )
                n_si.append( len(np.unique(S2Si_pk["nsipm"])) )
                evts.append( ev )

                nslides = len(S2[S2["peak"]==pk])
                sipms    = np.unique(S2Si_pk["nsipm"].values)

                b = S2Si_pk.index[0]
                #charge per slide
                for sl in range(0, int(nslides)-1):
                    q = []
                    for si in range(0, len(sipms)):
                        sl_si = S2Si_pk[S2Si_pk.index == b + sl + nslides*si]
                        q.append( sl_si["ene"].values )

                    Q_per_slide.append( np.sum(q) )

    si_df = pd.DataFrame({
                'event' : evts,
                'charge': Q   ,
                'touch' : n_si})

    qsl_df = pd.DataFrame({
                'charge_per_sl': Q_per_slide})

    si_df .to_hdf(outfilename, key='Q')
    qsl_df.to_hdf(outfilename, key='sl')


if __name__ == "__main__":
    Pmaps_SiSignal_info(pmapdir, npmaps, outfilename)

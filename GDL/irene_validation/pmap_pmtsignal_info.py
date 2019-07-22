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


def loop_in_events(Spmap, SPMTpmap, EVENTS):
    n, time, energy, height, width, rms, most_active_pmt, mact_percentage = [], [], [], [], [], [], [], []
    events = []

    for ev in EVENTS:
        S    = Spmap   [Spmap   ["event"]==ev]
        SPMT = SPMTpmap[SPMTpmap["event"]==ev]

        PEAKS = np.unique(S["peak"])
        if len(PEAKS)>0: n.append(np.max(PEAKS)+1)
        else:            n.append(0)

        for pk in PEAKS:
            #Total
            times = S[S["peak"]==pk]["time"].values
            enes  = S[S["peak"]==pk]["ene"] .values

            events.append(ev)
            time  .append(times[np.argmax(enes)]/10**3)
            height.append(np.max(enes))
            energy.append(np.sum(enes))
            width .append(times[-1]-times[0])

            PMTS  = np.unique(SPMT["npmt"])
            esum = []
            for pmt in PMTS:
                enes = SPMT[SPMT["npmt"]==pmt]["ene"].values
                esum.append( np.sum(enes[enes>0]) )
            most_active_pmt.append(PMTS[np.argmax(esum)])
            mact_percentage.append( np.max(esum)/np.sum(esum)*100)
    return events, n, time, height, energy, width, most_active_pmt , mact_percentage


def Pmaps_PMTSignal_info(pmapdir, npmaps, outfilename):
    n_events_in_pmap = []

    nS1s, time_S1, height_S1, energy_S1, width_S1, rms_S1, most_active_pmt_S1 = [], [], [], [], [], [], []
    nS2s, time_S2, height_S2, energy_S2, width_S2, rms_S2, most_active_pmt_S2 = [], [], [], [], [], [], []
    mact_percentage_S1, mact_percentage_S2 = [], []

    events_S1, events_S2 = [], []
    evts = []
    file_number = []

    FILES = glob.glob(pmapdir + "/*")
    FILES.sort()
    FILES = FILES[:npmaps]

    for pmap in FILES:

        if pmap.split('_')[-3]=="v0.9.9":
            file_number.append(int(pmap.split('/')[-1].split('_')[1]))
        else:
            file_number.append(int(pmap.split('_')[-1][:4]))


        S1pmap, S2pmap, _, S1PMTpmap, S2PMTpmap = load_pmaps_as_df(pmap)

        EVENTS = np.unique(S2pmap["event"].values)
        evts.extend(EVENTS)
        n_events_in_pmap.append( len(EVENTS) )

        ######### S1 DATA ###########
        events, n, time, height, energy, width, most_active_pmt, mact_per = loop_in_events(S1pmap, S1PMTpmap, EVENTS)

        nS1s.extend(n)
        events_S1.extend(events)
        time_S1.extend(time)
        height_S1.extend(height)
        energy_S1.extend(energy)
        width_S1.extend(width)
        most_active_pmt_S1.extend(most_active_pmt)
        mact_percentage_S1.extend(mact_per)

        ######### S2 DATA ############
        events, n, time, height, energy, width, most_active_pmt, mact_per = loop_in_events(S2pmap, S2PMTpmap, EVENTS)

        nS2s.extend(n)
        events_S2.extend(events)
        time_S2.extend(time)
        height_S2.extend(height)
        energy_S2.extend(energy)
        width_S2.extend(width)
        most_active_pmt_S2.extend(most_active_pmt)
        mact_percentage_S2.extend(mact_per)


    S1_df = pd.DataFrame({
                'event':  events_S1,
                'time':   time_S1,
                'height': height_S1,
                'energy': energy_S1,
                'width':  width_S1,
                'mactPMT': most_active_pmt_S1,
                'mact_perc': mact_percentage_S1})


    S2_df = pd.DataFrame({
                'event':  events_S2,
                'time':   time_S2,
                'height': height_S2,
                'energy': energy_S2,
                'width':  width_S2,
                'mactPMT':most_active_pmt_S2,
                'mact_perc': mact_percentage_S2})

    nS_by_event = pd.DataFrame({
                'event': evts ,
                'nS1s':   nS1s,
                'nS2s':   nS2s})

    nevent_by_pmap = pd.DataFrame({
                'file': file_number ,
                'nevent':   n_events_in_pmap})


    S1_df         .to_hdf(outfilename, key='S1')
    S2_df         .to_hdf(outfilename, key='S2')
    nS_by_event   .to_hdf(outfilename, key='nS')
    nevent_by_pmap.to_hdf(outfilename, key='nevent')



if __name__ == "__main__":
    Pmaps_PMTSignal_info(pmapdir, npmaps, outfilename)

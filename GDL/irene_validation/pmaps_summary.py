import glob
import numpy             as np
import pandas            as pd
import tables            as tb

from invisible_cities.io.pmaps_io import load_pmaps_as_df

import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i" , "--indir"       , type=str, help="pmapdir")
parser.add_argument("-r" , "--nfiles_range", type=int,  help="file range", nargs=2)
parser.add_argument("-o"  , "--out"        , type=str, help="outdir")
parser.add_argument("-sl"  , "--slidecut"     , type=int, help="Cut in # of files for slide data")
parser.add_argument("-si"  , "--sicut"        , type=int, help="Cut in # of files fos sipm data")

args = parser.parse_args(sys.argv[1:])

pmapdir     = args.indir
pmap_range  = args.nfiles_range
outfile     = args.out
sldcut      = args.slidecut
sicut       = args.sicut

def create_and_fill_summary_file(pmapdir, outfile, pmap_range, sldcut, sicut):

    #### CREATE FILE ####
    h5file = tb.open_file(outfile, mode="w", title="Pmap Summary")

    S1group = h5file.create_group("/", 'S1', title='S1 summary')
    S1table = h5file.create_table(S1group, 'S1', S1Signal, title="S1 table")

    S2group = h5file.create_group("/", 'S2', 'S2 summary')
    S2table = h5file.create_table(S2group, 'S2', S2Signal, title="S2 table")

    Nevgroup = h5file.create_group("/", 'N_events', 'Number of events per file')
    Nevtable = h5file.create_table(Nevgroup, 'Nevents', n_events, title="Number of events table")

    Sldgroup = h5file.create_group("/", 'Slide', 'Slide info')
    Sldtable = h5file.create_table(Sldgroup, 'Sld', slide_info, title="Slide info table")


    SIPMgroup = h5file.create_group("/", "SIPM", "Charge by Sipm")


    #### FILL FILE ####
    FILES = glob.glob(pmapdir + "/*")
    FILES.sort()
    start, stop = pmap_range[0], pmap_range[1]
    FILES = FILES[start : stop]

    processed = 1
    arr = np.ndarray(shape=(0, 2))
    for pmap in FILES:

        if pmap.split('_')[-3]=="v0.9.9":
            file_number = int(pmap.split('/')[-1].split('_')[1])
        else:
            file_number = int(pmap.split('_')[-1][:4])

        S1pmap, S2pmap, S2SIpmap, S1PMTpmap, S2PMTpmap = load_pmaps_as_df(pmap)
        EVENTS = np.unique(S2pmap["event"].values)

        #### Fill Number of events table ####
        Nev = Nevtable.row
        Nev["file_number"] = file_number
        Nev["n_events"]    = len(EVENTS)
        Nev.append()

        #### Fill S1s ####
        loop_in_events_S1(S1table.row, S1pmap, S1PMTpmap, EVENTS)

        #### Fill S1s ####
        if processed>sldcut: Sld = None
        else:                Sld = Sldtable.row
        loop_in_events_S2(S2table.row, Sld, S2pmap, S2PMTpmap, S2SIpmap, EVENTS, file_number)


        if processed<=sicut or sicut>=len(FILES):
            sipm_q = S2SIpmap[S2SIpmap["ene"]>0]
            arr = np.concatenate( (arr, sipm_q[["nsipm", "ene"]].values))

            if processed==sicut or processed==len(FILES):
                sipmarray = h5file.create_array(SIPMgroup, 'sipm_charge', arr, "SIPM charges")
                sipmarray.flush()

        processed += 1

    #### Save data to disk and close ####
    Nevtable .flush()
    S1table  .flush()
    S2table  .flush()
    Sldtable .flush()

    h5file.close()


def loop_in_events_S1(S, Spmap, SPMTpmap, EVENTS):
    for ev in EVENTS:
        Sgn  = Spmap   [Spmap   ["event"]==ev]
        SPMT = SPMTpmap[SPMTpmap["event"]==ev]

        PEAKS = np.unique(Sgn["peak"])
        for pk in PEAKS:
            #Total
            times = Sgn[Sgn["peak"]==pk]["time"].values
            enes  = Sgn[Sgn["peak"]==pk]["ene"] .values

            S["event"]  = ev
            S["time"]   = times[np.argmax(enes)]/10**3
            S["height"] = np.max(enes)
            S["energy"] = np.sum(enes)
            S["width"]  = times[-1]-times[0]

            PMTS  = np.unique(SPMT["npmt"])
            esum = []
            for pmt in PMTS:
                enes = SPMT[(SPMT["peak"]==pk)&(SPMT["npmt"]==pmt)]["ene"].values
                esum.append( np.sum( enes[enes>0]) )

            S["most_active_PMT"] = PMTS[np.argmax(esum)]
            S["energy_fraction_most_active_PMT"] = np.max(esum)/np.sum(esum)*100

            S.append()


def loop_in_events_S2(S, Sld, Spmap, SPMTpmap, SSIpmap, EVENTS, file_number):
    for ev in EVENTS:
        Sgn  = Spmap   [Spmap   ["event"]==ev]
        SPMT = SPMTpmap[SPMTpmap["event"]==ev]
        SSI  = SSIpmap [SSIpmap ["event"]==ev]

        PEAKS = np.unique(Sgn["peak"])
        for pk in PEAKS:
            #Total
            times = Sgn[Sgn["peak"]==pk]["time"].values
            enes  = Sgn[Sgn["peak"]==pk]["ene"] .values

            S["event"]  = ev
            S["file" ]  = file_number
            S["time"]   = times[np.argmax(enes)]/10**3
            S["height"] = np.max(enes)
            S["energy"] = np.sum(enes)
            S["width"]  = times[-1]-times[0]
            S["charge"]        = np.sum( SSI[ SSI["peak"] == pk ]["ene"] )
            S["touched_sipms"] = len(np.unique(SSI[ SSI["peak"] == pk ]["nsipm"]))

            PMTS  = np.unique(SPMT["npmt"])
            esum = []
            for pmt in PMTS:
                enes = SPMT[(SPMT["peak"]==pk)&(SPMT["npmt"]==pmt)]["ene"].values
                esum.append( np.sum( enes[enes>0]) )

            S["most_active_PMT"] = PMTS[np.argmax(esum)]
            S["energy_fraction_most_active_PMT"] = np.max(esum)/np.sum(esum)*100

            S.append()

            #slides
            if Sld:
                nslides = len( Sgn[Sgn["peak"]==pk] )
                sipms   = np.unique( SSI[ SSI["peak"] == pk ]["nsipm"] )
                if len(sipms)==0: continue

                splitted = np.array( np.split(SSI[ SSI["peak"] == pk ]["ene"].values, len(sipms)) ).T
                charge_per_slide = np.sum(splitted, axis=0)

                for slide in splitted:
                    Sld["event"]         = ev
                    Sld["charge"]        = np.sum( slide )
                    Sld["touched_sipms"] = len(slide[slide>0])
                    Sld.append()


class S1Signal(tb.IsDescription):
    event    = tb.Int64Col  (pos=0)
    time     = tb.Float64Col(pos=1)
    height   = tb.Float64Col(pos=2)
    energy   = tb.Float64Col(pos=3)
    width    = tb.Float64Col(pos=4)
    most_active_PMT = tb.Int64Col(pos=5)
    energy_fraction_most_active_PMT = tb.Float64Col(pos=6)

class S2Signal(tb.IsDescription):
    event    = tb.Int64Col  (pos=0)
    file     = tb.Int64Col  (pos=1)
    time     = tb.Float64Col(pos=2)
    height   = tb.Float64Col(pos=3)
    energy   = tb.Float64Col(pos=4)
    width    = tb.Float64Col(pos=5)
    most_active_PMT = tb.Int64Col(pos=6)
    energy_fraction_most_active_PMT = tb.Float64Col(pos=7)

    charge        = tb.Float64Col(pos=8)
    touched_sipms = tb.Int64Col  (pos=9)

class n_events(tb.IsDescription):
    file_number = tb.Int64Col(pos=0)
    n_events    = tb.Int64Col(pos=1)

class slide_info(tb.IsDescription):
    event         = tb.Int64Col  (pos=0)
    charge        = tb.Float64Col(pos=1)
    touched_sipms = tb.Int64Col  (pos=2)


if __name__ == "__main__":
    create_and_fill_summary_file(pmapdir, outfile, pmap_range, sldcut, sicut)

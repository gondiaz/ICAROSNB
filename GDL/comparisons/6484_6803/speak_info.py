import os
import sys
import argparse

import numpy  as np
import pandas as pd
import tables as tb
import matplotlib.pyplot as plt

from invisible_cities.io.pmaps_io import load_pmaps


parser = argparse.ArgumentParser()
parser.add_argument("-pd" , "--pmaps_dir" , type=str, help="pmaps directory")
parser.add_argument("-r"  , "--run-number", type=int, help="run number")
parser.add_argument("-n"  , "--n-pmaps"   , type=int, help="number of pmaps to compute")
parser.add_argument("-tg" , "--trigger"   , type=int, help="trigger type: 1 or 2")

args = parser.parse_args(sys.argv[1:])

pmapsdir = args.pmaps_dir
run      = args.run_number
n_pmaps  = args.n_pmaps
trigger  = args.trigger


def Speak_info(pmapsdir, run, n_pmaps, trigger):
    '''
    Arguments:

    pmapsdir: directory of the pmaps to be computed
    run: run number
    n_pmaps: number of pmaps to analyce

    Output:

    Creation of h5 file with SPeaks data.

    Comment:

    The output is redundant, since the number of S1 and S2 could be
    calculated from SPeak_event_number number of appearances

    '''

    S1_time, S1_height, S1_energy, S1_charge, S1_width, S1_rms = [], [], [], [], [], []
    S2_time, S2_height, S2_energy, S2_charge, S2_width, S2_rms = [], [], [], [], [], []
    S_pmap_number = []

    S1_event_number, S2_event_number = [], []
    Pmap_number, Times, Rates = [], [], []


    i = 0
    for root, dirs, files in os.walk(pmapsdir):
        for filename in files:
            try:
                pmap = load_pmaps(pmapsdir + '/' + filename)
                with tb.open_file(pmapsdir + '/' + filename, 'r') as h5f:
                    event_time = h5f.root.Run.events.read()
                    events = np.array([et[0] for et in event_time])
                    times  = np.array([et[1] for et in event_time])
            except:
                continue

            Pmap_number.append(int(filename.split('_')[1]))
            Times.append(np.mean(times))
            Rates.append(len(events)/(times.max()-times.min()))

            for event in pmap:

                for s1 in pmap[event].s1s:

                    S1_event_number.append(event)
                    # S1_number.append(len(pmap[event].s1s))
                    S1_time.append(s1.time_at_max_energy)
                    S1_height.append(s1.height)
                    S1_energy.append(s1.total_energy)
                    S1_charge.append(s1.total_charge)
                    S1_width.append(s1.width)
                    S1_rms.append(s1.rms)

                for s2 in pmap[event].s2s:

                    S_pmap_number.append(int(filename.split('_')[1]))

                    S2_event_number.append(event)
                    # S2_number.append(len(pmap[event].s2s))
                    S2_time.append(s2.time_at_max_energy)
                    S2_height.append(s2.height)
                    S2_energy.append(s2.total_energy)
                    S2_charge.append(s2.total_charge)
                    S2_width.append(s2.width)
                    S2_rms.append(s2.rms)
            i+=1
            if i>=n_pmaps: break

    S1_df = pd.DataFrame({
                'S1_event_number': S1_event_number,
                # 'S1_number': S1_number,
                'S1_time': S1_time,
                'S1_height': S1_height,
                'S1_energy': S1_energy,
                'S1_charge': S1_charge,
                'S1_width': S1_width,
                'S1_rms': S1_rms})

    S2_df = pd.DataFrame({
                'S2_event_number': S2_event_number,
                'Pmap_number': S_pmap_number,
                # 'S2_number': S2_number,
                'S2_time': S2_time,
                'S2_height': S2_height,
                'S2_energy': S2_energy,
                'S2_charge': S2_charge,
                'S2_width': S2_width,
                'S2_rms': S2_rms})

    Rates_df = pd.DataFrame({
                'Pmap_number': Pmap_number,
                'Time': Times ,
                'Rate': Rates})


    datafilename = f'SPeaks_info_run{run}_trigger{trigger}.h5'

    S1_df   .to_hdf(datafilename, key='S1')
    S2_df   .to_hdf(datafilename, key='S2')
    Rates_df.to_hdf(datafilename, key='Rates')


if __name__ == "__main__":
    Speak_info(pmapsdir, run, n_pmaps, trigger)

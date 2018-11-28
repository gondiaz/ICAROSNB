##PBS options

#PBS -N Corrections
#PBS -q long
#PBS -M gonzalodiazlopez10@gmail.com
#PBS -m bae
#PBS -o /data5/users/gdiaz/corrections/corr.log
#PBS -e /data5/users/gdiaz/corrections/corr.err

echo Current directory : $PWD

. /data4/NEXT/users/gdiaz/Software/miniconda3/etc/profile.d/conda.sh
cd /data5/users/gdiaz/Software/IC

echo Current directory : $PWD

conda deactivate
conda activate IC-3.7-2018-10-20
export ICTDIR=/data5/users/gdiaz/Software/IC/
export ICDIR=$ICTDIR/invisible_cities/
export PYTHONPATH=$ICTDIR
export PATH=$ICTDIR/bin:$PATH

export IC_DATA="/data5/users/gdiaz/DATA"
export CSTHDIR="/data5/users/gdiaz/Software/CsTh"
export KRCALIB="/data5/users/gdiaz/Software/KrCalib"
export PYTHONPATH=$CSTHDIR:$KRCALIB:$PYTHONPATH

echo Date: $(date)

cd /data5/users/gdiaz/corrections

time python clarice.py -it pmaps -r 6482 -p 0 12000 -id /analysis/6482/hdf5/prod/v0.9.9/20181011/pmaps/trigger2 -od ./DATA -cf /data5/users/gdiaz/DATA/maps/corrections_run6482.h5 -tf trigger2_v0.9.9_20181011_krth1300

echo Date: $(date)

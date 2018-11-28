##PBS options

#PBS -N blobcalc
#PBS -q long
#PBS -M gonzalodiazlopez10@gmail.com
#PBS -m bae
#PBS -o /data5/users/gdiaz/blobcalc/blobcalc.log
#PBS -e /data5/users/gdiaz/blobcalc/blobcalc.err

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

cd /data5/users/gdiaz/blobcalc

time python blobcalc.py -r 6206 -ty Tlds -cd ../Corrections/6206 -pd ../event_selection/DATA/6206/pmaps/ -El 390000 410000 -tg {tag} -rf {rx} {ry} -zd {zd} -R {R}

echo Date: $(date)

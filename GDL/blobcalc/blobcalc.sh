##PBS options

#PBS -N {run}_R{R}
#PBS -q long
#PBS -M gonzalodiazlopez10@gmail.com
#PBS -m bae
#PBS -o /data5/users/gdiaz/blobcalc/res.log
#PBS -e /data5/users/gdiaz/blobcalc/err.err

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
export ICAROSDIR="/data5/users/gdiaz/Software/ICAROS"
export PYTHONPATH=$ICAROSDIR:$PYTHONPATH

echo Date: $(date)

cd /data5/users/gdiaz/blobcalc

time python blobcalc.py -r {run} -cf {cfnam} -pd {pdir} -tg {tag} -kr /data5/users/gdiaz/DATA/maps/ -El {Ea} {Eb} -R {R}

echo Date: $(date)

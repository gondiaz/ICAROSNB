import os

#template = open("template.sh").read()
#for i, param in enumerate(params):
#    job_filename = "job_{}.sh".format(i)
#    open(job_filename, "w").write(template.format(param=param))
#    os.chmod(job_filename, 777)
#    os.system("qsub " + job_filename)

template = open("blobcalc.sh").read()


Rad = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
Ea, Eb = 410000, 445000

run = 6482
corr_filenam = "/data5/users/gdiaz/corrections/DATA/cepks_{0}_0000_11999_6q0min.h5".format(run)
pmaps_dir    = "/analysis/{0}/hdf5/prod/v0.9.9/20181011/pmaps/trigger2".format(run)
tag    = "trigger2_v0.9.9_20181011_krth1300"

for R in Rad:
    job_filename = "./jobs/blob_{0}_{1}_{2}_{3}.sh".format(run, Ea, Eb, R)
    open(job_filename, "w").write(template.format(run=run, cfnam=corr_filenam, pdir=pmaps_dir ,tag=tag,
                                                    Ea=Ea, Eb=Eb, R=R))

    os.chmod(job_filename, 777)
    os.system("qsub " + job_filename)

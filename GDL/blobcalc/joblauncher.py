import os

#template = open("template.sh").read()
#for i, param in enumerate(params):
#    job_filename = "job_{}.sh".format(i)
#    open(job_filename, "w").write(template.format(param=param))
#    os.chmod(job_filename, 777)
#    os.system("qsub " + job_filename)

template = open("blobcalc.sh").read()

r = [1]*11
zd= [-1]*11
R = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
tag = pk

for r, zd, R in zip(r, zd, R):
    job_filename = "./jobs/blob_{0}_{1}_{2}_{3}.sh".format(tag, r, zd, R)
    open(job_filename, "w").write(template.format(tag=tag , rx=r, ry=r, zd=zd, R=R))

    os.chmod(job_filename, 777)
    os.system("qsub " + job_filename)

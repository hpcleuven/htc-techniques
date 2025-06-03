#!/bin/bash -l
#PBS -l nodes=1
#PBS -L tasks=32:lprocs=4
#PBS -l walltime=1:00:00
#PBS -N worker_32_tasks
#PBS -q cpu_milan

cd $PBS_O_WORKDIR

module load R-bundle-CRAN/2024.11-foss-2024a
export OMP_NUM_THREADS=4

LOGFILE="$PBS_JOBNAME-$(printf '%03d' $PBS_ARRAYID).log"
echo "SIZE=$SIZE" >> $LOGFILE
start=$(date +%s%3N)

# two work itesm each using 4 cores on one socket
Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --matrix_size=$SIZE

end=$(date +%s%3N)
echo "Elapsed time (msec): $((end - start))" >> $LOGFILE

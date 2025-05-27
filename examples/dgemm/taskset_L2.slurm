#!/bin/bash -l
#SBATCH --cluster=wice
#SBATCH --partition=batch_sapphirerapids
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --ntasks-per-socket=4
#SBATCH --cpus-per-task=12
#SBATCH --time=5:00
#SBATCH --job-name=taskset_L2
#SBATCH --output=%x-%j.log

module load R-bundle-CRAN/2024.11-foss-2024a
export OMP_NUM_THREADS=4

start=$(date +%s%3N)

# two work itesm each using 4 cores on one socket
taskset -c 0-3   Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
taskset -c 12-15 Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
taskset -c 24-27 Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
taskset -c 36-39 Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
taskset -c 48-51 Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
taskset -c 60-63 Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
taskset -c 72-75 Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
taskset -c 84-87 Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
wait

end=$(date +%s%3N)
elapsed=$((end - start))
echo "Elapsed time: $elapsed (milliseconds)"

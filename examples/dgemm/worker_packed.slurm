#!/bin/bash -l
#SBATCH --cluster=wice
#SBATCH --partition=batch_sapphirerapids
#SBATCH --nodes=1
#SBATCH --ntasks=24
#SBATCH --cpus-per-task=4
#SBATCH --time=1:00:00
#SBATCH --job-name=worker_packed

module load R-bundle-CRAN/2024.11-foss-2024a
export OMP_NUM_THREADS=4

start=$(date +%s%3N)

# two work itesm each using 4 cores on one socket
Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --matrix_size=$SIZE

end=$(date +%s%3N)
echo "Elapsed time (msec): $((end - start))"

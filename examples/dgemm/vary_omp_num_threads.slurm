#!/bin/bash -l
#SBATCH --cluster=wice
#SBATCH --partition=batch_sapphirerapids
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=96
#SBATCH --time=1:00:00
#SBATCH --job-name=vary_omp_num_threads
#SBATCH --output=%x.log

module load R/4.4.2-gfbf-2024a
module load R-bundle-CRAN/2024.11-foss-2024a

for threads in 1 2 4 8 16 32 48 64 96; do
    export OMP_NUM_THREADS=$threads
    echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"
    time Rscript dgemm.R -n 1 -s 3000 -p 20 -c 1
done

#!/bin/bash -l
#SBATCH --cluster=wice
#SBATCH --partition=batch_sapphirerapids
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=96
#SBATCH --time=1:00:00
#SBATCH --job-name=vary_power
#SBATCH --output=%x.log

module load R/4.4.2-gfbf-2024a
module load R-bundle-CRAN/2024.11-foss-2024a

export OMP_NUM_THREADS=4

for p in 10 20 30 40 50 60; do
    echo "power=$p"
    time Rscript dgemm.R -n 1 -s 3333 -p $p -c 1
done

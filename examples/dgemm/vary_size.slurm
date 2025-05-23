#!/bin/bash -l
#SBATCH --cluster=wice
#SBATCH --partition=batch_sapphirerapids
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=96
#SBATCH --time=1:00:00
#SBATCH --job-name=vary_size
#SBATCH --output=%x.log

module load R/4.4.2-gfbf-2024a
module load R-bundle-CRAN/2024.11-foss-2024a

export OMP_NUM_THREADS=4

for s in 33 100 333 1000 3333 10000; do
    echo "SIZE=$s"
    time Rscript dgemm.R -n 1 -s $s -p 60 -c 1
done

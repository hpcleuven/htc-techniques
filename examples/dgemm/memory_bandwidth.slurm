#!/bin/bash -l
#SBATCH --cluster=wice
#SBATCH --partition=batch_sapphirerapids
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=96
#SBATCH --time=5:00
#SBATCH --job-name=memory_bandwidth
#SBATCH --output=%x-%j.log

module load R-bundle-CRAN/2024.11-foss-2024a
export OMP_NUM_THREADS=4

start=$(date +%s%3N)

for i in $(seq 1 24); do
    Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --size=3333 &
done
wait

end=$(date +%s%3N)
elapsed=$((end - start))
echo "Elapsed time: $elapsed (milliseconds)"

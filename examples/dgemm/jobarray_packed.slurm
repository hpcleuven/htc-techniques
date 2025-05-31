#!/bin/bash -l
#SBATCH --cluster=wice
#SBATCH --partition=batch_sapphirerapids
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=15:00
#SBATCH --job-name=jobarray_packed

module load R-bundle-CRAN/2024.11-foss-2024a
export OMP_NUM_THREADS=4

INPUT_FILE=input_jobarray.csv
echo "Slurm array task id: $SLURM_ARRAY_TASK_ID"
LINENUM=$SLURM_ARRAY_TASK_ID
SIZE=$(awk "NR==$LINENUM" $INPUT_FILE)
echo "SIZE=$SIZE"

start=$(date +%s%3N)

# two work itesm each using 4 cores on one socket
Rscript dgemm.R --nr_matrices=1 --nr_cores=1 --power=60 --matrix_size=$SIZE

end=$(date +%s%3N)
echo "Elapsed (msec): $((end - start))"

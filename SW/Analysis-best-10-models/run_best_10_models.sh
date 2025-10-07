#!/bin/bash
#SBATCH --partition=workq
#SBATCH --job-name=analyze2
#SBATCH --nodes=1
#SBATCH --time=00:60:00
#SBATCH --account=k10077
#SBATCH --exclusive
#SBATCH --err=job_%j.err
#SBATCH --output=job_%j.out
ulimit -s unlimited

module load python/3.10.13


# Extract best 10 models from sorted files
tail -10   allmodels.sorted   >  list-best-10.inp
python3  ./getdescriptors.py     list-best-10.inp  >  list-best-10.dat

# find descriptors frequency
python3 ./count_descriptors.py  list-best-10.dat

# Slice the master CSV to extract small CSV corresponding to best 10 models
python3   ./slice_best_10_csv.py    Metal-050_51cats-BC.csv    list-best-10.dat

# Run MLR and LOOCV on the best 10 models
for CASE in best_01 best_02 best_03 best_04 best_05 \
            best_06 best_07 best_08 best_09 best_10
do

# Prepare and run MLR and LOOCV
   python3 ./invert_csv.py         $CASE.csv      5d-$CASE.csv
   python3 ./csv_2_matrix.py -c 5d-$CASE.csv
   python3 /scratch/cavalll/cobra/Tests/mlr.py -m 5d-$CASE.matrix
   python3 /scratch/cavalll/cobra/Tests/loo.py -m 5d-$CASE.matrix

# Prepare file to average MLR and LOO results
   grep Fit$ 5d-$CASE.mlr_out | awk '{print $2, $3, $4}' > 5d-$CASE.mlr_fit

   paste -d\   fit_all.dat   5d-$CASE.mlr_fit   > tmp
   mv tmp      fit_all.dat   

   paste -d\   loo_all.dat   5d-$CASE.loo_dat   > tmp
   mv tmp      loo_all.dat   
done

# Run average and standard deviation on the 10 models
python3 ./average_best_10_models.py  fit_all.dat  > averaged_fit.dat
python3 ./average_best_10_models.py  loo_all.dat  > averaged_loo.dat








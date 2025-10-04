echo "Linking .......... ", MLR version 2022-03-30

# --------------------------------------------------------------
# Compiling the MLR core requires that BLAS and LAPACK libraries
#
# commands to compile with gfortran or ifort are indicated below
# Uncomment the one matching your environment
#
# Eventually adapt at your environment.
# --------------------------------------------------------------

# -----------------------
# Compiling with gfortran
# -----------------------


#module load lapack/3.9.0/gnu-6.4.0
#gfortran -fsanitize=address -Og -o MLR.x MLR-2022-03-30.f  normalization*f dnormal*f -lblas -llapack
#gfortran -O3 -o MLR.x MLR-2022-03-30.f  normalization*f dnormal*f -lblas -llapack



# --------------------
# Compiling with ifort
# --------------------
ifort *.f -o MLR.x -Wl,--start-group \
             ${MKLROOT}/lib/intel64/libmkl_intel_lp64.a \
             ${MKLROOT}/lib/intel64/libmkl_core.a \
             ${MKLROOT}/lib/intel64/libmkl_sequential.a \
             -Wl,--end-group -lpthread -lm -ldl


# ----------------------------------
# Moving executable to bin directory
# ----------------------------------

mv MLR.x ../../bin/


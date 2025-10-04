** RFS 1.0 **
Luigi Cavallo - 2025

Download the whole the package in a given directory, possibly named RFS. <br>
Then, modify the script below.

** "SW/Python/run-mc-filtered.py **
In this script change the line below to match the path where your code is. <br>
      mlr_path = "/scratch/cavalll/RFS/SW/Fortran/MLR-intel.x"

<br>
<br>

Then, move to your running directory and copy there the script below:

** run-mc-100M.sh **

Main script to be copied to your working directory. Three lines to be modified:<br>

Change the initial lines to match your project, username, etc.

Change the line below to match the directory where all the SW is stored:<br>
RFSHOME=/scratch/cavalll/RFS/

Line below: 

    python3   $RFSHOME/Python/run-mc-filtered.py  myfile.csv 5 10 $SEED  --maxpw 0.80 > Metal-050_51cats-BC-5d.$SEED &

5 is the number of descriptors to include.

10 is the number of combinations to test.  For real runs should be 1000000

--maxpw 0.80 sets the maximum pairwise correlation allowed between the selected descriptors.


Second instance to change, line below, same parameters as above:

    python3   $RFSHOME/Python/run-mc-filtered.py  myfile.csv 5 10 9880590681   --maxpw 0.80 > Metal-050_51cats-BC-5d.9880590681

<br> 


Additional files to run the job. Examples in the Examples directory<br>

** matrix.head **
Example of control file specifying the job details<br>
 <br>

** myfile.csv ** <br>
Your CSV file, following format<br>
Line 0: headers line <br>
Col 1: System labels <br>
Col 2: Target values <br>
Col 3-N: Descripotrs <br>

** sterics.dat ** <br>
Dummy empty file, needed for input compatibility. Soon will be removed.<br>


<br>
<br>

As you have in your dir the CSV file, matrix.head, sterics.dat and run-mc-100M.sh submit the job as:

sbatch run-mc-100M.sh

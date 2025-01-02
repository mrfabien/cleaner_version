#!/bin/bash -l

#SBATCH --mail-type END
#SBATCH --mail-user fabien.augsburger@unil.ch
#SBATCH --chdir /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/data/climatology
#SBATCH --job-name hm_clim_storms
#SBATCH --output /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/climatology/log/con/con-%A_%a.out
#SBATCH --error /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/climatology/log/error/err-%A_%a.err
#SBATCH --partition cpu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 1
#SBATCH --mem 64G
#SBATCH --time 00:30:00
#SBATCH --array=0-185

# Set your environment
module purge
dcsrsoft use 20240303
module load gcc
source ~/.bashrc
conda activate /work/FAC/FGSE/IDYST/tbeucler/default/fabien/conda_env

# Specify the path to the config file
config=/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/climatology/config_climato_winter.txt
# echo "SLURM_ARRAY_TASK_ID is :${SLURM_ARRAY_TASK_ID}" >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/curnagl/case_study/output_test_all.txt

# Extract the nom_var for the current $SLURM_ARRAY_TASK_ID
month=$(awk -v ArrayTaskID=${SLURM_ARRAY_TASK_ID} '$1==ArrayTaskID {print $2}' $config)

# Extract the annee for the current $SLURM_ARRAY_TASK_ID
day=$(awk -v ArrayTaskID=${SLURM_ARRAY_TASK_ID} '$1==ArrayTaskID {print $3}' $config)

# see if the nom_var and annee are correctly extracted 

# echo "var is :"$nom_var >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/curnagl/case_study/output_test.txt
# echo "annee is :"$annee >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/curnagl/case_study/output_test.txt

# Execute the python script
python3 /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/util/climatology/hm_clim_with_storms.py "$month" "$day"

# Print to a file a message that includes the current $SLURM_ARRAY_TASK_ID, the same variable, and the year of the sample
#echo "This is array task ${SLURM_ARRAY_TASK_ID}, the variable name is ${nom_var} and the year is ${annee}. Level is ${level}" >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/data/climatology/log/output_dm_without_storm.txt
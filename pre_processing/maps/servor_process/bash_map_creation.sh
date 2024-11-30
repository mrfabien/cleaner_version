#!/bin/bash -l

#SBATCH --mail-type END
#SBATCH --mail-user fabien.augsburger@unil.ch
#SBATCH --chdir /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/maps
#SBATCH --job-name map_creation
#SBATCH --output /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/maps/logs/con/con-%A_%a.out
#SBATCH --error /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/maps/logs/error/err-%A_%a.err
#SBATCH --partition cpu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 1
#SBATCH --mem 64G
#SBATCH --time 00:30:00
#SBATCH --array=0-31

module purge
dcsrsoft use 20240303
module load gcc
source ~/.bashrc
conda activate /work/FAC/FGSE/IDYST/tbeucler/default/fabien/conda_env

# Specify the path to the config file
config=/work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/maps/config_map_creation_years.txt
# echo "SLURM_ARRAY_TASK_ID is :${SLURM_ARRAY_TASK_ID}" >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/curnagl/case_study/output_test_all.txt

id=${SLURM_ARRAY_TASK_ID}

# Extract the nom_var for the current $SLURM_ARRAY_TASK_ID
#nom_var=$(awk -v ArrayTaskID=${SLURM_ARRAY_TASK_ID} '$1==ArrayTaskID {print $2}' $config)

# Extract the annee for the current $SLURM_ARRAY_TASK_ID
annee=$(awk -v ArrayTaskID=${SLURM_ARRAY_TASK_ID} '$1==ArrayTaskID {print $2}' $config)

# Extract the level for the current $SLURM_ARRAY_TASK_ID
#level=$(awk -v ArrayTaskID=${SLURM_ARRAY_TASK_ID} '$1==ArrayTaskID {print $4}' $config)

# see if the nom_var and annee are correctly extracted 

# echo "var is :"$nom_var >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/curnagl/case_study/output_test.txt
# echo "annee is :"$annee >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/curnagl/case_study/output_test.txt

# Execute the python script by looping from 0 to 95 (number of storms)

python3 /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/cleaner_version/pre_processing/maps/map_creation_bash.py "$annee" # "$nom_var" "$annee" "$level"

# Print to a file a message that includes the current $SLURM_ARRAY_TASK_ID, the same variable, and the year of the sample
#echo "This is array task ${SLURM_ARRAY_TASK_ID}, the variable name is ${nom_var} and the year is ${annee}. Level is ${level}" >> /work/FAC/FGSE/IDYST/tbeucler/default/fabien/repos/curnagl/case_study/output_all.txt
## Installation
```
conda env create -f env.yml
```

## Git Bash
```
source /c/Users/Admin/miniconda3/etc/profile.d/conda.sh
```

## Powershell/cmd
```
conda activate tio2-s2ef
```

## Run a few scripts
```
python scripts/preprocessing/01_download_metadata.py
python scripts/preprocessing/02_filter_tio2_systems.py
python scripts/preprocessing/03_download_s2ef_data.py
python scripts/preprocessing/04_create_tio2_lmdb.py
python scripts/preprocessing/05_compute_statistics.py
```

## If you want to update any packages in env.yml
```
conda env update -f env.yml -n tio2-s2ef
```

## Uninstall conda env
```
conda env remove --name tio2-s2ef-v1
```


```
conda env list
```

An Environment that works for fairchem v1:
https://github.com/facebookresearch/fairchem/blob/fairchem_core-1.7.0/packages/env.cpu.yml
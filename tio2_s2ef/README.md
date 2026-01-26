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
python src/preprocessing/01_download_metadata.py
python src/preprocessing/02_filter_tio2_systems.py
python src/preprocessing/03_download_s2ef_data.py
python src/preprocessing/04_create_tio2_lmdb.py
python src/preprocessing/05_compute_statistics.py
```

### Data structure after step 04
```
data/
├── metadata/
├── raw/
│   ├── 200k
│   ├── 2M
│   ├── 20M
│   └── all
├── uncompressed_data/
│   ├── 200k
│   ├── 2M
│   ├── 20M
│   └── all
└── tio2_lmddb/
    ├── 200k
    ├── 2M
    ├── 20M
    └── all
```

## Use to convert extxyz.txt and xyz.txt into lmdb
```
python -m scripts.preprocess_ef --data-path "D:/extxyz.txt_xyz.txt_dir" --out-path "D:/lmdb_dir" --num-workers 8
```
```
python -m scripts.preprocess_ef --data-path "D:/Data44" --out-path "D:/Data44_processed" --num-workers 8
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
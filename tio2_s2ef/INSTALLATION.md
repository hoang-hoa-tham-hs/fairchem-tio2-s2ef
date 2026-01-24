# Manual Installation Guide for TiO2-S2EF Project

This guide provides step-by-step instructions to set up the complete development environment for the TiO2-S2EF project.

## Prerequisites

- Conda/Miniconda installed on your system
- Python >=3.9, <3.13

---

## Step 1: Create and Activate Conda Environment

Create a new conda environment named `tio2-s2ef` with Python 3.9:

```bash
conda create -n tio2-s2ef python=3.9 -y
```

Activate the environment:

```bash
conda activate tio2-s2ef
```

---

## Step 2: Install Core Dependencies

Install scientific computing and data processing libraries from conda-forge:

```bash
conda install -c conda-forge ase python-lmdb numpy scipy pandas matplotlib seaborn tqdm jupyter pyyaml wandb numba tensorboard -y
```

---

## Step 3: Install PyTorch and Geometric Libraries

Install PyTorch geometric dependencies with CPU support. These packages require specific PyG wheels from the official PyG repository:

```bash
pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
pip install torch_cluster==1.6.3+pt24cpu --find-links https://data.pyg.org/whl/torch-2.4.0+cpu.html
pip install torch_geometric==2.5.3
pip install pyg-lib==0.4.0+pt24cpu --find-links https://data.pyg.org/whl/torch-2.4.0+cpu.html
pip install torch_scatter==2.1.2+pt24cpu --find-links https://data.pyg.org/whl/torch-2.4.0+cpu.html
pip install torch_sparse==0.6.18+pt24cpu --find-links https://data.pyg.org/whl/torch-2.4.0+cpu.html
pip install torch_spline_conv==1.2.2+pt24cpu --find-links https://data.pyg.org/whl/torch-2.4.0+cpu.html
```

---

## Step 4: Verify Installation

Verify that PyTorch and related packages are correctly installed:

```bash
conda list torch
```

**Expected output (or similar):**

```
Name                     Version          Build            Channel     
torch                      2.4.1            pypi_0           pypi        
torch-cluster              1.6.3+pt24cpu    pypi_0           pypi        
torch-geometric            2.5.3            pypi_0           pypi        
torch-scatter              2.1.2+pt24cpu    pypi_0           pypi        
torch-sparse               0.6.18+pt24cpu   pypi_0           pypi        
torch-spline-conv          1.2.2+pt24cpu    pypi_0           pypi        
```

---
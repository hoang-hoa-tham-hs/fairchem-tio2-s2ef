from pathlib import Path


class BasePath:
    """Base directory paths"""
    # Project root (where README.md, environment.yml)
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    
    # Main directories
    SCRIPTS_DIR = PROJECT_ROOT / "scripts"
    CONFIGS_DIR = PROJECT_ROOT / "configs"
    NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
    TESTS_DIR = PROJECT_ROOT / "tests"
    DOCS_DIR = PROJECT_ROOT / "docs"


class DataPath:
    """Data-related paths"""
    # Base data directory
    DATA_DIR = BasePath.PROJECT_ROOT / "data"
    
    # Raw data directories
    RAW_DIR = DATA_DIR / "raw"
    RAW_S2EF_DIR = RAW_DIR / "s2ef"
    
    # Processed data directories
    PROCESSED_DIR = DATA_DIR / "processed"
    
    # TiO2-specific data directories
    TIO2_DIR = DATA_DIR / "tio2"
    TIO2_TRAIN_DIR = TIO2_DIR / "train"
    TIO2_VAL_DIR = TIO2_DIR / "val"
    
    # Metadata directory
    METADATA_DIR = DATA_DIR / "metadata"
    
    # Specific metadata files
    OC20_MAPPING_FILE = METADATA_DIR / "oc20_data_mapping.pkl"
    TIO2_MAPPING_FILE = METADATA_DIR / "tio2_data_mapping.pkl"
    TIO2_SYSTEM_IDS_FILE = METADATA_DIR / "tio2_system_ids.txt"
    TIO2_STATISTICS_FILE = METADATA_DIR / "tio2_statistics.json"
    TIO2_NORMALIZATION_FILE = METADATA_DIR / "tio2_normalization_stats.json"


class OutputPath:
    """Output paths for models, results, logs"""
    # Model checkpoints
    MODELS_DIR = BasePath.PROJECT_ROOT / "models"
    CHECKPOINTS_DIR = BasePath.PROJECT_ROOT / "checkpoints"
    
    # Results and logs
    RESULTS_DIR = BasePath.PROJECT_ROOT / "results"
    LOGS_DIR = BasePath.PROJECT_ROOT / "logs"


class S2EFDataPath:
    """S2EF dataset specific paths"""
    
    @staticmethod
    def get_split_dir(split="200k", dataset_type="train"):
        """
        Get directory for specific split and dataset type
        
        Args:
            split: "200k", "2M", "20M", or "all"
            dataset_type: "train" or "val"
        
        Returns:
            Path to the split directory
        """
        return DataPath.RAW_S2EF_DIR / split / dataset_type
    
    @staticmethod
    def get_split_lmdb(split="200k", dataset_type="train"):
        """
        Get LMDB path for specific split
        
        Args:
            split: "200k", "2M", "20M", or "all"
            dataset_type: "train" or "val"
        
        Returns:
            Path to data.lmdb file
        """
        return S2EFDataPath.get_split_dir(split, dataset_type) / "data.lmdb"
    
    @staticmethod
    def get_tar_file(split="200k", dataset_type="train"):
        """
        Get tar file path for download
        
        Args:
            split: "200k", "2M", "20M", or "all"
            dataset_type: "train" or "val"
        
        Returns:
            Path to .tar file
        """
        if dataset_type == "train":
            filename = f"s2ef_train_{split.upper()}.tar"
        else:
            filename = "s2ef_val_20K.tar"
        
        return DataPath.RAW_DIR / filename


class DownloadURLs:
    """URLs for downloading data"""
    BASE_URL = "https://dl.fbaipublicfiles.com/opencatalystproject/data"
    
    # OC20 metadata
    OC20_METADATA_URL = f"{BASE_URL}/oc20_data_mapping.pkl"
    
    # S2EF dataset URLs
    S2EF_URLS = {
        "200k": {
            "train": f"{BASE_URL}/s2ef_train_200K.tar",
            "val": f"{BASE_URL}/s2ef_val_20K.tar",
        },
        "2M": {
            "train": f"{BASE_URL}/s2ef_train_2M.tar",
            "val": f"{BASE_URL}/s2ef_val_20K.tar",
        },
        "20M": {
            "train": f"{BASE_URL}/s2ef_train_20M.tar",
            "val": f"{BASE_URL}/s2ef_val_20K.tar",
        },
        "all": {
            "train": f"{BASE_URL}/s2ef_train_all.tar",
            "val": f"{BASE_URL}/s2ef_val_20K.tar",
        }
    }
    
    @staticmethod
    def get_s2ef_url(split="200k", dataset_type="train"):
        """Get download URL for S2EF data"""
        return DownloadURLs.S2EF_URLS[split][dataset_type]
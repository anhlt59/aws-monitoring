#!/usr/bin/python
from pathlib import Path
import json
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AGENT_CONFIG_DIR = BASE_DIR / "infra" / "agent" / "configs"
MASTER_CONFIG_DIR = BASE_DIR / "infra" / "master" / "configs"
METADATA_PATH = BASE_DIR / "statics" / "metadata_test.json"


def load_project_info(file_path):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return {
        "name": data.get("Name", ""),
        "account_id": data.get("Account", ""),
        "region": data.get("Region", "")
    }


def create_metadata():
    metadata = []
    
    for file in AGENT_CONFIG_DIR.glob("*.yml"):
        project_info = load_project_info(file)
        metadata.append(project_info)
    
    for file in MASTER_CONFIG_DIR.glob("*.yml"):
        project_info = load_project_info(file)
        metadata.append(project_info)
    
    return metadata


def save_metadata(metadata, path=METADATA_PATH):
    with open(path, "w") as f:
        json.dump(metadata, f, indent=4)



if __name__ == "__main__":
    metadata = create_metadata()
    save_metadata(metadata)

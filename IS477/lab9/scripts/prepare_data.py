"""
IS477 Data Management, Curation, and Reproducibilty

This script downloads and verifies the following datasets prior to analysis:

  Becker, Barry and Kohavi, Ronny. (1996). Adult.
  UCI Machine Learning Repository.
  https://doi.org/10.24432/C5XW20.

  Ding, F., Hardt, M., Miller, J., & Schmidt, L. (2021).
  Retiring Adult: New Datasets for Fair Machine Learning.
  Advances in Neural Information Processing Systems, 34, 6478–6490.
"""

import requests
import os
import hashlib
import zipfile

def unzip(path_to_zip, target_path): 
    print (f"Unzipping {path_to_zip}")
    with zipfile.ZipFile(path_to_zip) as z:
        z.extractall(target_path)

def download_and_validate(url, path, expected_hash):

    response = requests.get(url)
    response.raise_for_status()

    if not os.path.exists(path):
        base_dir = os.path.dirname(path)
        print(f"Creating directory for {path}")
        os.makedirs(base_dir, exist_ok=True)

    with open(path, mode="wb") as f:
        f.write(response.content)

    with open(path, mode="rb") as f:
        data = f.read()
        computed_hash = hashlib.sha256(data).hexdigest()

    if computed_hash != expected_hash:
        print(f"WARNING: Computed hash does not match expected has for {path}")
    else:
        print(f"INFO: Computed hash matches expected hash for {path}")

# UCI Adult Dataset https://doi.org/10.24432/C5XW20
uci_adult_path = "data/adult.zip"
uci_adult_url = "https://archive.ics.uci.edu/static/public/2/adult.zip"
uci_adult_expected_hash = "7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb"

# Folktables Adult reconstructed dataset
reconstruction_url = "https://raw.githubusercontent.com/socialfoundations/folktables/main/adult_reconstruction.csv"
reconstruction_expected_hash = "4895fd481e7ae6e2ca423e6213454b39f0f7ec0efcd741ad2f6c667554f0eb51"
reconstrution_path = "data/folktables/adult_reconstruction.csv"

# Download, validate, and extract the UCI Adult dataset
download_and_validate(uci_adult_url, uci_adult_path, uci_adult_expected_hash)
unzip(uci_adult_path, "data/adult")

# Download and validate the Folktables Adult reconstruction dataset
download_and_validate(reconstruction_url, reconstrution_path, reconstruction_expected_hash, )
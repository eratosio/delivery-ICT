import logging
import tempfile
import os
import json
import zipfile
from constant import ORG_ID, ORG_NAME
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_manifest():

    logger.info(f"Creating manifest.json for {ORG_NAME}")

    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join("sample_manifest", "manifest.json"), "r") as f:
            manifest = json.load(f)
            manifest["organisationId"] = ORG_ID
            manifest["models"][0]["id"] = f"eratos.sandbox.calculate_sap_flow_{ORG_ID}"
            manifest["models"][0]["name"] = f"Eratos Sap Flow Model: Calculate Updated SAP flow for {ORG_NAME}"


        with open("manifest.json", "w") as f:
            json.dump(manifest, f, indent=4)

    logger.info(f"Finish creating manifest.json for {ORG_NAME}")


def zip_files(file_paths, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            if os.path.exists(file):
                arcname = os.path.basename(file)  # Only keep filename, not full path
                zipf.write(file, arcname)
                print(f"Added: {file}")
            else:
                print(f"Skipped (not found): {file}")

if __name__ == "__main__":
    generate_manifest()
    files_to_zip = [
        "constant.py",
        "manifest.json",
        "entry.py"
    ]

    # 👇 Output zip file
    output_zip = "Archive.zip"

    zip_files(files_to_zip, output_zip)
    print(f"Archive created: {output_zip}")
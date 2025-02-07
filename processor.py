import glob
import os

import requests


from main import get_pdf_data, open_encrypted_pdf

PASSWORD = "..."  # If your utility PDFs have a password
PATH = "/mnt/bills/"
HA_TOKEN = "..."  # Long lived access token from Home Assistant


def update_ha(value, host="127.0.0.1", port=8123, token=HA_TOKEN):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    url = f"http://{host}:{port}/api/services/input_number/set_value"
    payload = {"entity_id": "input_number.electricity_pricing", "value": value}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def process_pdf(filepath):
    pdf = open_encrypted_pdf(filepath, PASSWORD)
    billing_period, kwh_cost = get_pdf_data(pdf)
    return (billing_period, kwh_cost)


if __name__ == "__main__":
    print("Processing files")
    filepaths = glob.glob(PATH + "*.pdf")
    for filepath in filepaths:
        print("Processing ", filepath)
        # We don't actually use billing_period for anything. I was hoping I
        # could set historical sensor values with an HA API call but that
        # doesn't seem to be the case.
        billing_period, kwh_cost = process_pdf(filepath)
        print(f"Got {kwh_cost} for {billing_period}, updating HA")
        update_ha(kwh_cost)
        # Only rename once HA has been updated
        os.rename(filepath, filepath.replace(".pdf", ".bak"))

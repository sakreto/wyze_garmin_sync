#!/usr/local/bin/python3
import math
import os
import datetime
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError
from fit import FitEncoder_Weight
import hashlib
import garth
from getpass import getpass

def load_env(env_file='creds.env'):
    os.chdir("wyze_garmin_sync")
    with open(env_file) as file:
        for line in file:
            if line.startswith('#') or not line.strip():
                continue
            # Split on the first equals and strip spaces
            key, value = map(str.strip, line.split('=', 1))
            os.environ[key] = value

load_env()

WYZE_EMAIL = os.getenv('WYZE_EMAIL')
WYZE_PASSWORD = os.getenv('WYZE_PASSWORD')
WYZE_KEY_ID = os.getenv('WYZE_KEY_ID')
WYZE_API_KEY = os.getenv('WYZE_API_KEY')
GARMIN_USERNAME = os.getenv('GARMIN_USERNAME')
GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')

# Global variables for start and end dates
# Example start date: January 1, 2024
START_DATE = datetime.datetime(2023, 9, 13)
# Example end date: February 1, 2024
END_DATE = datetime.datetime(2023, 12, 9)


def login_to_wyze():
    try:
        response = Client().login(email=WYZE_EMAIL, password=WYZE_PASSWORD,
                                  key_id=WYZE_KEY_ID, api_key=WYZE_API_KEY)
        access_token = response.get('access_token')
        return access_token
    except WyzeApiError as e:
        print(f"Wyze API Error: {e}")
        return None


def upload_to_garmin(file_path):
    try:
        garth.resume('tokens')
        garth.client.username
    except:
        try:
            garth.login(GARMIN_USERNAME, GARMIN_PASSWORD)
            garth.save('tokens')
        except:
            email = input("Enter Garmin email address: ")
            password = getpass("Enter Garmin password: ")
            try:
                garth.login(email, password)
                garth.save('tokens')
            except Exception as exc:
                print(repr(exc))
                exit()

    try:
        with open(file_path, "rb") as f:
            garth.client.upload(f)
        return True
    except Exception as e:
        print(f"Garmin upload error: {e}")
        return False


def generate_fit_file(record, dry_run=False):
    fit = FitEncoder_Weight()
    timestamp = math.trunc(record.measure_ts / 1000)
    weight_in_kg = record.weight * 0.45359237

    data_keys = {
        'percent_fat': record.body_fat,
        'percent_hydration': record.body_water,
        'visceral_fat_mass': record.body_vfr,
        'bone_mass': record.bone_mineral,
        'muscle_mass': record.muscle,
        'basal_met': record.bmr,
        'physique_rating': record.body_type or 5,
        'active_met': record.bmr,
        'metabolic_age': record.metabolic_age,
        'visceral_fat_rating': record.body_vfr,
        'bmi': record.bmi
    }

    data = {key: float(value) if value is not None else None for key,
            value in data_keys.items()}
    if data.get('basal_met') is None:
        data['active_met'] = None
    else:
        data['active_met'] = int(float(record.bmr) * 1.25)

    # Add the data to the FIT encoder
    fit.write_file_info(time_created=timestamp)
    fit.write_file_creator()
    fit.write_device_info(timestamp=timestamp)
    fit.write_weight_scale(
        timestamp=timestamp,
        weight=weight_in_kg,
        percent_fat=data.get('percent_fat'),
        percent_hydration=data.get('percent_hydration'),
        visceral_fat_mass=data.get('visceral_fat_mass'),
        bone_mass=data.get('bone_mass'),
        muscle_mass=data.get('muscle_mass'),
        basal_met=data.get('basal_met'),
        physique_rating=data.get('physique_rating'),
        active_met=data.get('active_met'),
        metabolic_age=data.get('metabolic_age'),
        visceral_fat_rating=data.get('visceral_fat_rating'),
        bmi=data.get('bmi'),
    )
    fit.finish()

    # Define the directory and unique file paths based on record's timestamp

    fitfile_path = f"fitfiles/wyze_scale_{timestamp}.fit"

    if dry_run:
        print("Dry Run: Generated FIT file data for timestamp {}: ".format(timestamp))
        print(fit.getvalue())  # Print the content of the FIT file
    else:
        # Directly write the file without checking for the directory
        with open(fitfile_path, "wb") as fitfile:
            fitfile.write(fit.getvalue())

    # Return the path for further processing (e.g., uploading)
    return fitfile_path


def main(dry_run=False):
    access_token = login_to_wyze()
    print(f"Current working directory: {os.getcwd()}")
    os.chdir("wyze_garmin_sync")
    print(f"Current working directory: {os.getcwd()}")

    if access_token:
        client = Client(token=access_token)
        devices = client.devices_list()
        # print(f"Found devices: {devices}")

        for device in devices:
            if device.type == "WyzeScale":
                scale = client.scales.info(device_mac=device.mac)
                print(f"Scale found with MAC {device.mac}. Latest record is:")
                print(f"Body Type: {scale.latest_records[0].body_type or 5}")

                try:
                    historical_data = client.scales.get_records(
                        device_model=device.mac,
                        start_time=START_DATE,
                        end_time=END_DATE
                    )
                    print(
                        f"Number of historical records fetched: {len(historical_data)}")
                except Exception as e:
                    print(f"Error fetching historical data: {e}")
                    historical_data = []

                for record in historical_data:
                    print(
                        f"{'Dry Run: ' if dry_run else ''}Processing record for {record}")

                    generate_fit_file(record, dry_run=dry_run)
                    print("Fit data generated...")

                    if not dry_run:
                        fitfile_path = generate_fit_file(
                            record, dry_run=dry_run)
                        # Extract the timestamp from the record to name the checksum file
                        timestamp = math.trunc(record.measure_ts / 1000)
                        cksum_file_path = f"cksum/cksum_{timestamp}.txt"

                        with open(fitfile_path, "rb") as fitfile:
                            cksum = hashlib.md5(fitfile.read()).hexdigest()

                        upload_needed = False

                        if os.path.exists(cksum_file_path):
                            with open(cksum_file_path, "r") as cksum_file:
                                stored_cksum = cksum_file.read().strip()

                            if cksum != stored_cksum:
                                print("New measurement detected. Uploading file...")
                                upload_needed = True
                            else:
                                print("No new measurement for this record.")
                        else:
                            print(
                                "No checksum detected for this record. Uploading fit file and creating checksum...")
                            upload_needed = True

                        if upload_needed:
                            if upload_to_garmin(fitfile_path):
                                print("File uploaded successfully.")
                                with open(cksum_file_path, "w") as cksum_file:
                                    cksum_file.write(cksum)
                            else:
                                print("File upload failed.")


if __name__ == "__main__":
    main(dry_run=False)  # Set dry_run to False to perform actual processing

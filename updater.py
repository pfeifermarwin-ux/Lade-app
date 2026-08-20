import argparse

parser = argparse.ArgumentParser(description="Lade-app-updater")
parser.add_argument("--current-programm", type=str, required=True, help="Path to the current program")
parser.add_argument("--new-version", type=str, required=True, help="New version to update to")

args = parser.parse_args()
print(args)
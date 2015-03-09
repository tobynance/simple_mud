import sys
import os
import glob
import subprocess

MIGRATION_FOLDER = os.path.join("mud", "migrations")
DATA_MIGRATION_FILE = os.path.join(MIGRATION_FOLDER, "0002_initial_data.py")
TEMP_DATA_MIGRATION_FILE = DATA_MIGRATION_FILE[:-3]
PYTHON = sys.executable


########################################################################
def main():
    subprocess.call([PYTHON, "manage.py", "flush", "--noinput"])
    if os.path.exists(DATA_MIGRATION_FILE):
        os.rename(DATA_MIGRATION_FILE, TEMP_DATA_MIGRATION_FILE)
    else:
        raise Exception("No Data migration file found: %s" % DATA_MIGRATION_FILE)
    try:
        for filename in (glob.glob1(MIGRATION_FOLDER, "*.py") + glob.glob1(MIGRATION_FOLDER, "*.pyc")):
            if filename == "__init__.py":
                continue
            print "Removing file '%s'" % filename
            os.remove(os.path.join(MIGRATION_FOLDER, filename))
        subprocess.call([PYTHON, "manage.py", "makemigrations"])
    finally:
        os.rename(TEMP_DATA_MIGRATION_FILE, DATA_MIGRATION_FILE)

    subprocess.call([PYTHON, "manage.py", "migrate"])


########################################################################
if __name__ == "__main__":
    main()

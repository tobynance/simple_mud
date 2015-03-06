import sys
import os
import glob
import subprocess

DB_FILE = "db.sqlite3"
MIGRATION_FOLDER = os.path.join("mud", "migrations")
DATA_MIGRATION_FILE = os.path.join(MIGRATION_FOLDER, "0002_initial_data.py")
TEMP_DATA_MIGRATION_FILE = DATA_MIGRATION_FILE[:-3]
PYTHON = sys.executable


########################################################################
def main():
    if os.path.exists(DATA_MIGRATION_FILE):
        os.rename(DATA_MIGRATION_FILE, TEMP_DATA_MIGRATION_FILE)
    else:
        raise Exception("No Data migration file found: %s" % DATA_MIGRATION_FILE)
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

        for filename in (glob.glob1(MIGRATION_FOLDER, "*.py") + glob.glob1(MIGRATION_FOLDER, "*.pyc")):
            if filename == "__init__.py":
                continue
            print "Removing file '%s'" % filename
            os.remove(os.path.join(MIGRATION_FOLDER, filename))
        subprocess.call([PYTHON, "manage.py", "makemigrations"])
        subprocess.call([PYTHON, "manage.py", "migrate"])
    finally:
        os.rename(TEMP_DATA_MIGRATION_FILE, DATA_MIGRATION_FILE)


########################################################################
if __name__ == "__main__":
    main()

import sys
import os
import glob
import subprocess

MIGRATION_FOLDER = os.path.join("mud", "migrations")
PYTHON = sys.executable


########################################################################
def main():
    subprocess.call([PYTHON, "manage.py", "flush", "--noinput"])
    for filename in (glob.glob1(MIGRATION_FOLDER, "*.py") + glob.glob1(MIGRATION_FOLDER, "*.pyc")):
        if filename == "__init__.py":
            continue
        print "Removing file '%s'" % filename
        os.remove(os.path.join(MIGRATION_FOLDER, filename))
    subprocess.call([PYTHON, "manage.py", "makemigrations"])

    subprocess.call([PYTHON, "manage.py", "migrate"])
    subprocess.call([PYTHON, "manage.py", "load_initial_data"])


########################################################################
if __name__ == "__main__":
    main()

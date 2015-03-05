export PYTHONPATH=/home/tnance/projects/muds/python/simple_mud:$PYTHONPATH
/home/tnance/.virtualenvs/simplemud/bin/celery --app=simple_mud.celery:app beat --loglevel=INFO

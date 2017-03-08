# Lodestone Installation

## For developers

Clone the project from the git repository.  For example:

    git clone https://github.com/CottageLabs/lodestone.git

get all the submodules

    cd lodestone
    git submodule update --init --recursive
    
This will initialise and clone the esprit and magnificent-octopus libraries, and their submodules in turn.

Create your virtualenv and activate it

    virtualenv /path/to/venv
    source /path/to/venv/bin/activate

Install the dependencies and this app in the correct order:

    pip install -r requirements.txt
    
Create your local config, using a copy of the template provided

    mv template.local.cfg local.cfg

You shoud then edit local.cfg, and set your install environment's configuration

To start the application, you'll also need to install it into the virtualenv just this first time

    pip install -e .

Then, start your app with

    python service/web.py

For production installation see README-PRODUCTION.md


For the deposit/poll scripts, to run these in their own terminal so you can monitor them, and you can start them each with their commands:

    python service/tasks/dataset_deposit.py

    python service/tasks/ethesis_deposit.py

    python service/tasks/dataset_poll.py

    python service/tasks/ethesis_poll.py

## Tear down and re-up on test server

git pull
git submodule update --init --recursive
pip install -r requirements.txt

source ../lodestone-venv/bin/activate

python service/tasks/task_status.py -v -r
python service/tasks/purge_tasks.py -m <ethesis|dataset> -j <job_id>

curl -XDELETE http://localhost:9200/lodestone

cd /mnt/stor-pri/lodestone-dev/data/
rm -r *

screen -r
python service/web.py

sudo supervisorctl restart sword:*
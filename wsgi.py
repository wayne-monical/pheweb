
import os, sys

# Add the pheweb package into the PYTHONPATH so that we can import it.
# This assumes that you cloned pheweb from github.  If you installed with pip, maybe this has no effect?
sys.path.insert(0, '/home/wmonical/miniconda3/envs/phewas_dev3/lib/python3.10/site-packages')

# `data_dir` is the directory that contains `config.py` and `generated-by-pheweb/`.
data_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PHEWEB_DATADIR'] = data_dir

# Load `config.py`.
config_filepath = os.path.join(data_dir, 'config.py')
assert os.path.exists(config_filepath)
import pheweb.conf
pheweb.conf.load_overrides_from_file(config_filepath)

# WSGI uses the variable named `application`.
from pheweb.serve.server import app as application

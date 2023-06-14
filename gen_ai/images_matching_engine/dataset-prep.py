#%%
PROJECT_ID = 'vtxdemos'  # <--- TODO: CHANGE THIS
LOCATION = 'us-central1' 

import json
import os
import time
import pandas as pd
import matplotlib.pylab as plt
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
# import scann

from IPython.display import clear_output, Image
from IPython.core.display import HTML 

from google.cloud import aiplatform as vertex_ai
# from google.cloud import bigquery
from google.cloud import storage

from google import auth
# from google.colab import auth as colab_auth # if using Colab
# colab_auth.authenticate_user()
# %%

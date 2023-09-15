"""Customized handler for Stable Diffusion 1.5."""
import base64
import logging
from io import BytesIO

import torch
from diffusers import EulerDiscreteScheduler
from diffusers import StableDiffusionPipeline
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)
model_id = 'runwayml/stable-diffusion-v1-5'


class ModelHandler(BaseHandler):

  def __init__(self):
    self.initialized = False
    self.map_location = None
    self.device = None
    self.use_gpu = True
    self.store_avg = True
    self.pipe = None

  def initialize(self, context):
    """Initializes the pipe."""
    properties = context.system_properties
    gpu_id = properties.get('gpu_id')

    self.map_location, self.device, self.use_gpu = \
      ('cuda', torch.device('cuda:' + str(gpu_id)),
       True) if torch.cuda.is_available() else \
        ('cpu', torch.device('cpu'), False)

    # Use the Euler scheduler here instead
    scheduler = EulerDiscreteScheduler.from_pretrained(model_id,
                                                       subfolder='scheduler')
    pipe = StableDiffusionPipeline.from_pretrained(model_id,
                                                   scheduler=scheduler,
                                                   torch_dtype=torch.float16)
    pipe = pipe.to('cuda')
    # Uncomment the following line to reduce the GPU memory usage.
    # pipe.enable_attention_slicing()
    self.pipe = pipe

    self.initialized = True

  def preprocess(self, requests):
    """Noting to do here."""
    logger.info('requests: %s', requests)
    return requests

  def inference(self, preprocessed_data, *args, **kwargs):
    """Run the inference."""
    images = []
    for pd in preprocessed_data:
      prompt = pd['prompt']
      images.extend(self.pipe(prompt).images)
    return images

  def postprocess(self, output_batch):
    """Converts the images to base64 string."""
    postprocessed_data = []
    for op in output_batch:
      fp = BytesIO()
      op.save(fp, format='JPEG')
      postprocessed_data.append(base64.b64encode(fp.getvalue()).decode('utf-8'))
      fp.close()
    return postprocessed_data
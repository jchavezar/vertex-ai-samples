import json
import requests
import textwrap
from typing import Tuple
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel, GenerationResponse
from proto.marshal.collections import repeated
from proto.marshal.collections import maps

class Functions:
    def __init__(self):
        pass

    def recurse_proto_repeated_composite(self, repeated_object):
        repeated_list = []
        for item in repeated_object:
            if isinstance(item, repeated.RepeatedComposite):
                item = self.recurse_proto_repeated_composite(item)
                repeated_list.append(item)
            elif isinstance(item, maps.MapComposite):
                item = self.recurse_proto_marshal_to_dict(item)
                repeated_list.append(item)
            else:
                repeated_list.append(item)

        return repeated_list

    def recurse_proto_marshal_to_dict(self, marshal_object):
        new_dict = {}
        for k, v in marshal_object.items():
            if isinstance(v, maps.MapComposite):
                v = self.recurse_proto_marshal_to_dict(v)
            elif isinstance(v, repeated.RepeatedComposite):
                v = self.recurse_proto_repeated_composite(v)
            new_dict[k] = v

        return new_dict

    def get_text(self, response: GenerationResponse):
        """Returns the Text from the Generation Response object."""
        part = response.candidates[0].content.parts[0]
        try:
            text = part.text
        except:
            text = None

        return text

    def get_function_name(self, response: GenerationResponse):
        return response.candidates[0].content.parts[0].function_call.name

    def get_function_args(self, response: GenerationResponse) -> dict:
        return self.recurse_proto_marshal_to_dict(response.candidates[0].content.parts[0].function_call.args)
import os
import json
import requests
from k import _
from langchain.tools import tool
from unstructured.partition.html import partition_html


class BrowserTools:
    # noinspection PyMethodParameters
    @tool("Search external (internet)")
    def search_internet(query):
        """Useful to search the internet about a given topic and return relevant results"""
        top_result_to_return = 4
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': _,
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()['organic']
        string = []
        for result in results[:top_result_to_return]:
          try:
              string.append('\n'.join([
                  f"Title: {result['title']}", f"Link: {result['link']}",
                  f"Snippet: {result['snippet']}", "\n-----------------"
              ]))
          except KeyError:
            next

        print(string)
        print(string)
        print(string)
        print(string)
        return '\n'.join(string)



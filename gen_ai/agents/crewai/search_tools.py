import requests
from bs4 import BeautifulSoup
from googlesearch import search
from langchain.tools import tool
from google.cloud import discoveryengine
import streamlit as st
from google.protobuf.json_format import MessageToDict

variables={
    "project":"vtxdemos",
    "location":"global",
    "region": "us-central1",
    "datastore": "financial-internal-docs_1706730313453"
}

class SearchTools():
    @tool("Search the internet")
    def search_internet(query):
      """Useful to search the internet 
      about a a given topic and return relevant results"""
      results = search(query, num_results=2)
      
      response = []
      for link in results:
          #print(f"{result}")
          page = requests.get(link).text
          soup = BeautifulSoup(page, 'html.parser')
    
          for script in soup(["script", "style"]):
                      script.extract() 
    
          page_text = soup.getText()
          response.append(page_text)
          st.info("nfl")
          st.info(''.join(response))
    
          return ''.join(response)
    
    @tool("Search financial internal documents about Google, Amazon and Microsoft")
    def search_rag(query):
        """Useful to search through internal documents"""

        vsearch_client = discoveryengine.SearchServiceClient()
        vsearch_serving_config = vsearch_client.serving_config_path(
            project=variables["project"],
            location=variables["location"],
            data_store=variables["datastore"],
            serving_config="default_search",)
        content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True),
        summary_spec = discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=2, include_citations=True),
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=2,
                max_extractive_segment_count=2))
        request = discoveryengine.SearchRequest(
            serving_config=vsearch_serving_config, query=query, page_size=2, content_search_spec=content_search_spec)                                                         
        response = vsearch_client.search(request)
        documents = [MessageToDict(i.document._pb) for i in response.results]
        context = []
        for i in documents:
            for ans in i["derivedStructData"]["extractive_answers"]:
                context.append(ans["content"])
        res = ''.join(context)
        print(res)
        return str(res)
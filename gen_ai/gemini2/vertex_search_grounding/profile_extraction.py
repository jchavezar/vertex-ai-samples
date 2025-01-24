#%%
import csv
import json

from google import genai
from google.genai import types
from typing import List

from google.api_core.client_options import ClientOptions
from google.protobuf.json_format import MessageToDict
from google.cloud import discoveryengine_v1 as discoveryengine

#%%

# VAIS (Vertex AI Search)
project_id = "vtxdemos"
location = "global"
engine_id = "linkedin"

client_options = (
    ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
    if location != "global"
    else None
)

def vais_search(prompt):
  client = discoveryengine.SearchServiceClient()
  serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"


  content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
      snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
          return_snippet=True
      ),
      summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
          summary_result_count=5,
          include_citations=True,
          ignore_adversarial_query=True,
          ignore_non_summary_seeking_query=True,
          model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
              version="stable",
          ),
      ),
  )

  request = discoveryengine.SearchRequest(
      serving_config=serving_config,
      query=prompt,
      page_size=10,
      content_search_spec=content_search_spec,
      query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
          condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
      ),
      spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
          mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
      ),
  )

  response = client.search(request)
  documents = [MessageToDict(i.document._pb) for i in response.results]
  return documents

documents = vais_search("Jesus Chavez at Google")

#%%]
# Creating CSV using Gemini 2.0 and VAIS (Vertex AI Search)
input_filepath = "./gemini2/vertex_search_grounding/sp_people.csv"  # Replace with your input file path
output_filepath = "./gemini2/vertex_search_grounding/sp_people_out_vais.csv"  # Replace with your output file path

encodings_to_try = ['utf-8', 'latin-1', 'utf-16']  # Add more encodings if needed

with open(output_filepath, "w", newline='', encoding='utf-8') as outfile:
  writer = csv.writer(outfile)
  writer.writerow(["first_name", "last_name", "company", "document_1", "document_2", "document_3", "document_4", "document_5"])

  for encoding in encodings_to_try:
    try:
      with open(input_filepath, "r", newline='', encoding=encoding) as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Read the header

        for n, row in enumerate(reader):
          try:
            prompt = row[0] + " " + row[2] + " worked at: " + row[3]
            print(prompt)
            documents = vais_search(prompt)
            print("length: " + str(len(documents)))
            document_data = []
            for enum, i in enumerate(documents):
              if enum < 5:
                name = i["derivedStructData"]["pagemap"]["metatags"][0]["profile:first_name"] + " " + \
                       i["derivedStructData"]["pagemap"]["metatags"][0]["profile:last_name"]
                title = i["derivedStructData"]["pagemap"]["metatags"][0]["og:title"]
                description = i["derivedStructData"]["pagemap"]["metatags"][0]["og:description"]
                url = i["derivedStructData"]["pagemap"]["metatags"][0]["og:url"]
                document_data.append(
                    json.dumps({"name": name, "title": title, "description": description, "url": url}))
            writer.writerow([row[0], row[2], row[3]] + document_data)
          except UnicodeDecodeError as e:
            print(f"Error processing row {n + 2} with encoding {encoding}: {e}")
            print(f"Problematic row content: {row}")
          except Exception as e:  # Catch other potential exceptions
            print(f"An unexpected error occurred on row {n+2}: {e}")

        break  # If successful with an encoding, stop trying others

    except UnicodeDecodeError as e:
      print(f"Failed to open file with encoding {encoding}: {e}")
    except Exception as e:
      print(f"An error occured with file opening {e}")

print("Processing complete.")

#%%
# Creating CSV using Gemini 2.0 and Google Search Grounding
client = genai.Client(
    vertexai=True,
    project="vtxdemos",
    location="us-central1"
)

system_instructions = """
Use your <google search grounding tool> to find website user profiles to respond the answer.
Only use your grounding to answer questions, if you don't have any match with your grounding just say so.


Extract the following information from the user profile below: {user_profile}

name: first_name + last_name
title: title in the company he works on
description: role in their company
url: where the information comes from

Output in json:
"""

model = "gemini-2.0-flash-exp"

def gemini_search(prompt: str):
  contents = [
      types.Content(
          role="user",
          parts=[
              types.Part.from_text("{user_profile}: "+prompt)
          ]
      )
  ]
  tools = [
      types.Tool(google_search=types.GoogleSearch())
  ]
  generate_content_config = types.GenerateContentConfig(
      system_instruction=system_instructions,
      tools=tools
  )
  res = client.models.generate_content(
      model = model,
      contents = contents,
      config = generate_content_config,
  )
  return res

_re = gemini_search("Jesus Chavez worked at: Google")

#%%
# Gemini 2.0 + Google Search Grounding v2

client = genai.Client(
    vertexai=True,
    project="vtxdemos",
    location="us-central1"
)

system_instructions_15 = """
* **Instructions**
Use the first and last name and the company from your search grounding to 
GET the first name and last name, company and description of the role and the source url/link

* **Rules**
- Be concise and just bring the result.

* **Output Expected**
- first name
- last name
- company
- description
- source url/link
"""
model = "gemini-2.0-flash-exp"

def gemini_search(name: str, company: str):
  contents = [
      types.Content(
          role="user",
          parts=[
              types.Part.from_text("""
              user_profile:
              Name: {name}
              Company: {company}
              """.format(name=name, company=company))
          ]
      )
  ]
  tools = [
      types.Tool(google_search=types.GoogleSearch())
  ]
  generate_content_config = types.GenerateContentConfig(
      system_instruction=system_instructions_15,
      tools=tools
  )
  res = client.models.generate_content(
      model = model,
      contents = contents,
      config = generate_content_config,
  )
  return res

_re = gemini_search(name="Hugh Lytle",company="Equality Health")
print(_re.text)

#%%
import csv

input_filepath = "./gemini2/vertex_search_grounding/sp_people_out_vais.csv"  # Replace with your input file path
output_filepath = "./gemini2/vertex_search_grounding/sp_people_out_gsearch.csv"  # Replace with your output file path

encodings_to_try = ['utf-8', 'latin-1', 'utf-16']  # Add more encodings if needed

with open(output_filepath, "w", newline='', encoding='utf-8') as outfile:
  writer = csv.writer(outfile)
  writer.writerow(["first_name","last_name", "company", "document_1", "document_2", "document_3", "document_4", "document_5", "gemini_out"])
  for encoding in encodings_to_try:
    try:
      with open(input_filepath, "r", newline='', encoding=encoding) as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Read the header

        for n, row in enumerate(reader):
          if n < 100:
            print(row)
            try:
              print(row[0]+row[1]+row[2]+row[3]+row[4]+row[5]+row[6])
              res = gemini_search(name=row[1]+" "+row[2], company=row[3])
              print(res.text)
              print("-"*80)
              writer.writerow(row + [res.text])
            except UnicodeDecodeError as e:
              print(f"Error processing row {n + 2} with encoding : {encoding}")
              print(f"Problematic row content: {row}")
            except Exception as e:  # Catch other potential exceptions
              print(f"An unexpected error occurred on row {n+2}: {e} with encoding: {encoding}")
          else:
            break
      break  # This break statement exits the encoding loop if the inner try block is successful


    except UnicodeDecodeError as e:
      print(f"Failed to open file with encoding : {encoding}")
    except Exception as e:
      print(f"An error occurred with file opening: {e}")
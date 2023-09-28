# %%
import io
import PIL
import time
import scann
import random
import base64
import PyPDF2
import vertexai
import concurrent
import numpy as np
from math import sqrt
import streamlit as st
from shapely import Polygon
from unidecode import unidecode
from google.cloud import documentai
import PIL.ImageFont, PIL.Image, PIL.ImageDraw
from google.cloud.documentai_v1 import Document
from vertexai.language_models import TextGenerationModel
from vertexai.preview.vision_models import MultiModalEmbeddingModel, Image


project_id = "vtxdemos"
location = "us"
docai_processor_id = "projects/254356041555/locations/us/processors/5f0b0deeb0a5d23b"
rate_limit_minute = 120
adjust_rate_limit = rate_limit_minute / 2

mm = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
vertexai.init(project="vtxdemos", location="us-central1")

st.title('Retrieval Augmented Generation (RAG) | Multimodal Embeddings')

#region Model Settings
settings = ["text-bison", "text-bison@001", "text-bison-32k"]
model = st.sidebar.selectbox("Choose a text model", settings)

temperature = st.sidebar.select_slider("Temperature", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.2) 
if model == "text-bison" or model == "text-bison@001":
        token_limit = st.sidebar.select_slider("Token Limit", range(1, 1025), value=256)
else:token_limit = st.sidebar.select_slider("Token Limit", range(1,8193), value=1024)
top_k = st.sidebar.select_slider("Top-K", range(1, 41), value=40)
top_p = st.sidebar.select_slider("Top-P", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], value=0.8) 
secret = st.sidebar.text_input("secret:", placeholder="ask: jesusarguelles@")

parameters =  {
    "temperature": temperature,
    "max_output_tokens": token_limit,
    "top_p": top_p,
    "top_k": top_k
    }
#endregion

#region set document_ai for ocr
docai_client = documentai.DocumentProcessorServiceClient(
    client_options = {"api_endpoint": f"{location}-documentai.googleapis.com"}
)
#endregion

#region streamlit file upload
uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")
if uploaded_file:
    source_document = uploaded_file.name
    pdf = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
    
    pdfs = []
    for page_num, page in enumerate(pdf.pages,1):
        writer = PyPDF2.PdfWriter()
        writer.add_page(page)
        with io.BytesIO() as bytes_stream:
            pdfs.append(writer.write(bytes_stream)[1].getbuffer().tobytes())
#endregion


    if secret == "test":
        #region read (ocr) each page and create metadata
    
        @st.cache_data
        def preprocessing(pdfs):

            def docai_run(p, start, raw_document):
                sleep_time = (p * (60/adjust_rate_limit)) - (time.time() - start)
                if sleep_time > 0: time.sleep(sleep_time)

                return docai_client.process_document(request = {"raw_document" : documentai.RawDocument(content=raw_document, mime_type = 'application/pdf'), "name" : docai_processor_id})

            #docai = lambda x : docai_client.process_document(request = {"raw_document" : documentai.RawDocument(content=x, mime_type = 'application/pdf'), "name" : docai_processor_id})

            results = []
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        docai_run,
                        p, start,
                        file
                    ) for p, file in enumerate(pdfs)
                ]
                for future in concurrent.futures.as_completed(futures):
                  results.append(Document.to_dict(future.result().document))

            documents = []
            page_images = []
            for r, result in enumerate(results):
                  results[r]['metadata'] = dict(vme_id = str(r))

                  document_image = PIL.Image.open(
                      io.BytesIO(
                          base64.decodebytes(result['pages'][0]['image']['content'].encode('utf-8'))
                          )
                      )
                  page_images.append(document_image)
                  tables = []
                  for t, table in enumerate(result['pages'][0]['tables']):
                      table_txt = ''
                      if 'text_anchor' in table['layout'].keys():
                        for s, segment in enumerate(table['layout']['text_anchor']['text_segments']):
                            if t == 0 and s == 0: start = 0
                            else: start = int(segment['start_index'])
                            end = int(segment['end_index'])
                            table_txt += result['text'][start:end]
                            table_txt.strip()
                            txt_size = 1000
                        # filtering out titles or any uniword
                        if len(table_txt) < 30:
                            continue
                        elif len(table_txt) > txt_size:
                            parts = len(table_txt)//txt_size+1
                            chunks, chunk_size = len(table_txt), len(table_txt)//parts
                            table_txt_split = {random.randint(0,100): table_txt[n:n+chunk_size] for n in range(0, chunks, chunk_size)}
                            for n, (key, val) in enumerate(table_txt_split.items()):
                                if len(val) < 30:
                                    continue
                                vertices = []
                                for vertex in table['layout']['bounding_poly']['normalized_vertices']:
                                    vertices.append(dict(x = vertex['x'] * document_image.size[0], y = vertex['y'] * document_image.size[1]))
                                tables.append(Polygon([(v['x'], v['y']) for v in vertices]))
                                documents.append(
                                    dict(
                                        page_content = val,
                                        metadata = dict(
                                            page = r+1,
                                            table = t+1,
                                            vme_id = str(len(documents)+key),
                                            filename = source_document,
                                            source_document = source_document
                                        ),
                                        extras = dict(
                                            #image = base64.decodebytes(result['pages'][0]['image']['content'].encode('utf-8')),
                                            vertices = vertices
                                        )
                                    )
                                )
                        else:
                            vertices = []
                            for vertex in table['layout']['bounding_poly']['normalized_vertices']:
                                vertices.append(dict(x = vertex['x'] * document_image.size[0], y = vertex['y'] * document_image.size[1]))
                            tables.append(Polygon([(v['x'], v['y']) for v in vertices]))
                            if len(table_txt) < 30:
                                continue
                            documents.append(
                                dict(
                                    page_content = table_txt,
                                    metadata = dict(
                                        page = r+1,
                                        table = t+1,
                                        vme_id = str(len(documents)),
                                        filename = source_document,
                                        source_document = source_document
                                    ),
                                    extras = dict(
                                        #image = base64.decodebytes(result['pages'][0]['image']['content'].encode('utf-8')),
                                        vertices = vertices
                                    )
                                )
                            ) 
                  for p, paragraph in enumerate(result['pages'][0]['paragraphs']):
                      paragraph_txt = ''
                      for s, segment in enumerate(paragraph['layout']['text_anchor']['text_segments']):
                          if p == 0 and s == 0: start = 0
                          else: 
                              start = int(segment['start_index'])
                              end = int(segment['end_index'])
                              paragraph_txt += result['text'][start:end+1]
                      if len(paragraph_txt) > 1000:
                          part_size = len(paragraph_txt)//1000+1
                          chunks, chunk_size = len(paragraph_txt), len(paragraph_txt)//part_size
                          paragraph_txt_split = {random.randint(0,100): paragraph_txt[n:n+chunk_size] for n in range(0, chunks, chunk_size)}
                          for key, val in paragraph_txt_split.items():
                              if len(val) < 40:
                                  continue
                              vertices = []
                              for vertex in paragraph['layout']['bounding_poly']['normalized_vertices']:
                                  vertices.append(dict(x = vertex['x'] * document_image.size[0], y = vertex['y'] * document_image.size[1]))
                              use_paragraph = True
                              for t_shape in tables:
                                  p_shape = Polygon([(v['x'], v['y']) for v in vertices])
                                  if p_shape.intersects(t_shape): use_paragraph = False
                              if use_paragraph:
                                  if paragraph_txt == "":
                                      continue
                                  documents.append(
                                      dict(
                                          page_content = val,
                                          metadata = dict(
                                              page = r+1,
                                              paragraph = p+1,
                                              vme_id = str(len(documents)+key),
                                              filename = source_document,
                                              source_document = source_document
                                              ),
                                          extras = dict(
                                              vertices = vertices
                                              )
                                          )
                                      )
                      else: 
                          vertices = []
                          for vertex in paragraph['layout']['bounding_poly']['normalized_vertices']:
                              vertices.append(dict(x = vertex['x'] * document_image.size[0], y = vertex['y'] * document_image.size[1]))
                              use_paragraph = True
                          for t_shape in tables:
                              p_shape = Polygon([(v['x'], v['y']) for v in vertices])
                              if p_shape.intersects(t_shape): 
                                  use_paragraph = False

                          if use_paragraph:
                              if len(paragraph_txt) < 30:
                                  continue
                              documents.append(
                                  dict(
                                      page_content = paragraph_txt,
                                      metadata = dict(
                                          page = r+1,
                                          paragraph = p+1,
                                          vme_id = str(len(documents)),
                                          filename = source_document,
                                          source_document = source_document
                                        ),
                                      extras = dict(
                                          vertices = vertices
                                          )
                                      )
                                  )
            return documents

        documents = preprocessing(pdfs)
        st.write(documents)
        #endregion

        #region Creating Embeddings for Document
        @st.cache_data
        def embeddings_database(documents):
            start = time.time()
            counter = 0
            for d, document in enumerate(documents):
                job_time = time.time() - start
                counter +=1
                if counter > 199 and job_time < 59:
                    time.sleep(60-job_time)
                    counter = 0
                    start = time.time()
                st.write(counter)
                st.write(job_time)
                documents[d]["embedding"] = mm.get_embeddings(contextual_text=document["page_content"]).text_embedding
            #st.write(documents)
            #endregion

            #region Using scann to create a Tensor compatible searcher

            # Create a numpy database to keep values
            index = np.empty((len(documents), len(documents[0]['embedding'])))

            if type(documents[0]['embedding']) == list:
                for i in range(index.shape[0]):
                    if documents[i]['page_content']:
                        index[i] = documents[i]['embedding']        
            elif type(documents[0]['embedding']) == np.ndarray: # retrieved from BigQuery
                for i in range(index.shape[0]):
                    if documents[i]['page_content']:
                        index[i] = documents[i]['embedding'].tolist()   

            normalized_index = index / np.linalg.norm(index, axis=1)[:, np.newaxis]
            return normalized_index, index

        normalized_index, index = embeddings_database(documents)

        builder = scann.scann_ops_pybind.builder(
            normalized_index, # index
            2, # num_neighbors
            "dot_product" # distance_measure
            )
        k = int(np.sqrt(index.shape[0]))
        st.write(index)
        st.write(index.shape[0])
        st.write(k)
        searcher = builder.tree(
            num_leaves=k, #num_leaves
            num_leaves_to_search=int(k/20), #num_leaves_to_search
            training_sample_size=index.shape[0]
            ).score_ah(
              2,
              anisotropic_quantization_threshold=0.2
              ).reorder(
                  index.shape[0]
                  ).build()

        def search_index(query, k):
            neighbors, distances = searcher.search(query, final_num_neighbors=k)
            return list(zip(neighbors, distances))

        selected = st.text_input("From prompt to embeddings 👇",)
        button_clicked = st.button("OK")
        text_search = selected
        text_search = unidecode(text_search.lower())

        if text_search:
            qe = mm.get_embeddings(contextual_text=text_search).text_embedding
            st.write(qe)
            st.write(search_index(qe, 2))

            score = search_index(qe, k = 1)[0][1]
            print(score)
            relevant_documentation = search_index(qe, k = 1 + 2*int(10*(1-score)))

            print(relevant_documentation)
            context = "\n".join([f'Context {c+1}:\n' + documents[doc[0]]['page_content'] for c, doc in enumerate(relevant_documentation)])
            st.write(context)
            st.write(relevant_documentation)
            #st.write()

            #region Using LLM (text-bison)

            model = TextGenerationModel.from_pretrained(model)
            response = model.predict(
                f"""Give a detailed answer to the question using information from the provided contexts.

                    {context}

                    Question:
                    {text_search}
                """,
                **parameters
            )
            st.write(f"Response from Model: {response.text}")
            #endregion

        #endregion
    else: st.write("You need to add the secret before continue...")
# %%    

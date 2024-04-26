#%%
import base64
import os
import io
import time
import scann
import numpy as np
from flet import *
import pandas as pd
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import HarmCategory, HarmBlockThreshold
from vertexai.language_models import TextEmbeddingModel
from langchain.text_splitter import RecursiveCharacterTextSplitter

light_primary = colors.BLUE_300

model_emb = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

def extraction(filename):
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.5,
        "top_p": 0.95,
    }

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # PDF into base64
    with open(filename, 'rb') as f:
        text = base64.b64encode(f.read())

    document1 = Part.from_data(
        mime_type="application/pdf",
        data=base64.b64decode(text))

    prompt = """
    Instructions:
     * Analyze Thoroughly:  Pay close attention to every element of the tax form (1065 or others), including text, checkboxes, tables, headers, footers, and any additional fields.
     * Contextualize: Understand the meaning and purpose of each section and field within the context of the specific tax form.
     * Relationships: Identify connections between different fields, sections, and tables. Consider how data in one part of the form may relate to information elsewhere.
     * Be Exhaustive: Extract every detail, no matter how small or seemingly insignificant. Even minor elements can be crucial for tax compliance.
     * Checkboxes: Be extremely meticulous in determining whether a checkbox is checked, unchecked, or partially filled. Look for any indication of a mark, even if it's faint, imperfect, or outside the designated box.
    Extraction Tasks:
     * Textual Data: Extract all text, including labels, instructions, numbers, amounts, dates, and written descriptions.
     * Checkboxes: Capture the checked/unchecked state of each checkbox.
     * Tables:
       * Extract data from each cell (both headers and values).
       * Note the relationships between rows and columns.
     * Key-Value Pairs: Identify all key-value pairs and extract both the key and its corresponding value.
     * Headers/Footers: Extract any information from headers and footers, such as page numbers, dates, or identifying information.
     * Always add additional metadata information like page number.
    Output Format:
     * Structured Markdown: Use Markdown syntax to organize the extracted data into sections, key-value pairs, and tables. Maintain clear headers, consistent formatting, and use Markdown's table features for tabular data.
    Example:
    ## Form Type: 1065
    ## Tax Year: 2023
    ## Business Name: Example LLC
    ## Page: 1
    
    ### Income
    * Gross receipts or sales: 100000
    * Returns and allowances: 5000
    * ... 
    
    """

    model = GenerativeModel("gemini-1.5-pro-preview-0409")
    response = model.generate_content(
        [prompt, document1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True
    )

    response_chunks = []

    try:
        for _ in response:
            print("Extracting still, bear with me...")
            response_chunks.append(_.text)
        final_response = "".join(response_chunks)
    except:
        final_response = f"There was a problem with the extraction."
        print(list(response))
        page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
            .content.content.controls.append(Text("There was a problem with the extraction", bgcolor=colors.RED_50, color=colors.BLACK))
        page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()

    return final_response


def split_docs(response: str, chunk_size=500, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    lang_docs = [lang_doc for lang_doc in text_splitter.create_documents([response])]
    return lang_docs


def create_embeddings(documents: str):
    start = time.time()
    pp = 0
    docs_with_emb = []
    if len(documents) < 2000:
        page_size = 1000
    else: page_size = 2000

    chunk_size = 500
    chunk_overlap = 20

    for i in range(0, len(documents), page_size):
        for n in range(0, len(documents[i:i+page_size]), chunk_size-chunk_overlap):
            print("loop2", n)
            rate_limit_minute = 550
            pp += 1
            sleep_time = (pp*(60/rate_limit_minute)) - (time.time()-start)
            if sleep_time > 0:
                time.sleep(sleep_time)
            chunk_doc = documents[n:n+chunk_size]
            docs_with_emb.append({f"chunk_text": chunk_doc, "content": documents[i:i+page_size], "embedding": model_emb.get_embeddings([chunk_doc])[0].values})
    return docs_with_emb


def run(filename, page):
    page.controls[0].content.controls[1].content.controls[1].content.controls[1]\
        .content.content.controls.append(
        Text("Processing your file, please wait...",
             color=colors.BLACK, bgcolor=colors.PURPLE_50))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    doc = []
    start = time.time()
    # if type(filename) == str:
    #     images = convert_from_path(filename)
    # else:
    #     images = convert_from_bytes(filename.getvalue())

    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(
        Text("From files to image pages finished in: {:.2f} s".format(time.time()-start),
             bgcolor=colors.GREY_50, color=colors.BLACK))

    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Gemini 1.5 Extraction please wait...", bgcolor=colors.PURPLE_50, color=colors.BLACK))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()

    cp_time = time.time()
    start_extraction = time.time()
    extracted_doc = extraction(filename)

    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Extraction finished in: {:.2f} s".format(time.time()-start),
                                              bgcolor=colors.GREY_50, color=colors.BLACK))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Using gecko for embeddings please wait...",  bgcolor=colors.PURPLE_50, color=colors.BLACK))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()
    cp_time = time.time()
    docs_with_emb = create_embeddings(extracted_doc)
    df = pd.DataFrame(docs_with_emb)
    if os.path.exists("realtime_table.pkl"):
        os.remove("realtime_table.pkl")
    else:
        pass
    df.to_pickle("realtime_table.pkl")

    # Local Vector Database with ScaNN

    img = np.array([r["embedding"] for i, r in df.iterrows()])
    k = int(np.sqrt(df.shape[0]))

    if int(k/20) < 1:
        leave_search = 1
    else:
        leave_search = int(k/20)

    start = time.time()

    print(start)

    print(df)
    print(df.shape[0])

    searcher = scann.scann_ops_pybind.builder(img, num_neighbors=5, distance_measure="squared_l2").tree(
        num_leaves=k, num_leaves_to_search=leave_search, training_sample_size=df.shape[0]).score_brute_force(
        2).reorder(7).build()

    print("scann built")

    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Embeddings finished in: {:.2f} s".format(time.time()-start),
                                              bgcolor=colors.GREY_50, color=colors.BLACK))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1] \
        .content.content.controls.append(Text("Enjoy!", bgcolor="#6200EA"))
    page.controls[0].content.controls[1].content.controls[1].content.controls[1].content.content.update()

    return searcher, extracted_doc

# query = model_emb.get_embeddings(["What's the total income?"])[0].values
# result = asyncio.run(vector_database_client.query(query, rag_schema))
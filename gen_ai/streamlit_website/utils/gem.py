import os
import glob
import fitz
from vertexai.generative_models import Image
from vertexai.language_models import TextEmbeddingModel


class Multimodal:
    def __init__(self, iterable=(), **kwargs) -> None :
        self.__dict__.update(iterable, **kwargs)
        self.text_embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
        print(self.pdf_folder_path)

    def get_document_metadata(self):
        for pdf_path in glob.glob(self.pdf_folder_path + "/3eleven_resident_handbook.pdf"):
            doc, num_pages = self.get_pdf_doc_object(pdf_path)
            file_name = pdf_path.split("/")[-1]
            text_metadata: Dict[Union[int, str], Dict] = {}
            image_metadata: Dict[Union[int, str], Dict] = {}

            print(num_pages)

            for page_num in range(num_pages):
                print(f"Processing page: {page_num + 1}")

                page = doc[page_num]

                try :
                    text = page.get_text()
                    (text, page_text_embeddings_dict, chunked_text_dict, chunk_embeddings_dict) = self.get_chunk_text_metadata(page)

                    text_metadata[page_num] = {
                        "text": text,
                        "page_text_embeddings": page_text_embeddings_dict,
                        "chunked_text_dict": chunked_text_dict,
                        "chunk_embeddings_dict": chunk_embeddings_dict,
                    }

                except:
                    text_metadata[page_num] = {
                        "text": "no text found on page",
                        "page_text_embeddings": "",
                        "chunked_text_dict": "",
                        "chunk_embeddings_dict": "",
                    }

                images = page.get_images()
                image_metadata[page_num] = {}
                print(images)

                for image_no, image in enumerate(images):
                    image_number = int(image_no + 1)
                    image_metadata[page_num][image_number] = {}

                    image_for_gemini, image_name = self.get_image_for_gemini(
                        doc, image, image_no, self.image_save_dir, file_name, page_num
                    )

                    print(
                        f"Extracting image from page: {page_num + 1}, saved as: {image_name}"
                    )

        return text, page_text_embeddings_dict, chunked_text_dict, chunk_embeddings_dict

    def get_pdf_doc_object(self, pdf_path):
        doc: fitz.Document = fitz.open(pdf_path)
        num_pages: int = len(doc)
        return doc, num_pages

    def get_chunk_text_metadata(self, page):
        character_limit = 1000
        overlap = 100
        embedding_size = 128

        text = page.get_text().encode("ascii", "ignore").decode("utf-8", "ignore")
        page_text_embeddings_dict = self.get_page_text_embedding(text)
        chunked_text_dict = self.get_text_overlapping_chunk(text, character_limit, overlap)
        chunk_embeddings_dict = self.get_page_text_embedding(chunked_text_dict)
        return text, page_text_embeddings_dict, chunked_text_dict, chunk_embeddings_dict

    def get_page_text_embedding(self, text_data):
        embeddings_dict = {}
        if isinstance(text_data, dict):
            # Process each chunk
            # print(text_data)
            for chunk_number, chunk_value in text_data.items():
                text_embd = self.get_text_embedding_from_text_embedding_model(text=chunk_value)
                embeddings_dict[chunk_number] = text_embd
        else:
            # Process the first 1000 characters of the page text
            text_embd = self.get_text_embedding_from_text_embedding_model(text=text_data)
            embeddings_dict["text_embedding"] = text_embd

        return embeddings_dict

    def get_text_embedding_from_text_embedding_model(self, text):
        embeddings = self.text_embedding_model.get_embeddings([text])
        text_embedding = [embedding.values for embedding in embeddings][0]
        return text_embedding

    def get_text_overlapping_chunk(self, text, character_limit, overlap):
        if overlap > character_limit:
            raise ValueError("Overlap cannot be larger than character limit.")

        # Initialize variables
        chunk_number = 1
        chunked_text_dict = {}

        # Iterate over text with the given limit and overlap
        for i in range(0, len(text), character_limit - overlap):
            end_index = min(i + character_limit, len(text))
            chunk = text[i:end_index]

            # Encode and decode for consistent encoding
            chunked_text_dict[chunk_number] = chunk.encode("ascii", "ignore").decode(
                "utf-8", "ignore"
            )

            # Increment chunk number
            chunk_number += 1

        return chunked_text_dict

    def get_image_for_gemini(self, doc, image, image_no, image_save_dir, file_name, page_num):
        xref = image[0]
        pix = fitz.Pixmap(doc, xref)
        pix.tobytes("jpeg")
        image_name = f"{image_save_dir}/{file_name}_image_{page_num}_{image_no}_{xref}.jpeg"
        os.makedirs(image_save_dir, exist_ok=True)
        print("TESTING")
        print(os.listdir(image_save_dir))
        print("TESTING")
        pix.save(image_name)
        image_for_gemini = Image.load_from_file(image_name)
        return image_for_gemini, image_name

info = {
    "pdf_folder_path": "../files",
    "image_save_dir": "tmp_images"
}

c = Multimodal(info)
text, page_text_embeddings_dict, chunked_text_dict, chunk_embeddings_dict = c.get_document_metadata()
print(text)
print(page_text_embeddings_dict)
print(chunked_text_dict)
print(chunk_embeddings_dict)

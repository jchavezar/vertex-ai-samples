from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore

def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    mime_type: str,
    file_path: str,
    field_mask: Optional[str] = None,
    processor_version_id: Optional[str] = None,
) -> None:
  # You must set the `api_endpoint` if you use a location other than "us".
  opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
  print("8"*80)
  print(file_path)

  client = documentai.DocumentProcessorServiceClient(client_options=opts)

  if processor_version_id:
    # The full resource name of the processor version, e.g.:
    # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
    name = client.processor_version_path(
        project_id, location, processor_id, processor_version_id
    )
  else:
    # The full resource name of the processor, e.g.:
    # `projects/{project_id}/locations/{location}/processors/{processor_id}`
    name = client.processor_path(project_id, location, processor_id)

  # Read the file into memory
  with open(file_path, "rb") as image:
    image_content = image.read()

  # Load binary data
  raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

  # For more information: https://cloud.google.com/document-ai/docs/reference/rest/v1/ProcessOptions
  # Optional: Additional configurations for processing.
  process_options = documentai.ProcessOptions(
      # Process only specific pages
      individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
          pages=[1]
      )
  )

  # Configure the process request
  request = documentai.ProcessRequest(
      name=name,
      raw_document=raw_document,
      field_mask=field_mask,
      process_options=process_options,
  )

  result = client.process_document(request=request)

  # For a full list of `Document` object attributes, reference this page:
  # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
  document = result.document

  all_blocks = []

  def extract_text_recursive(block):
      """Recursively extracts text from a block and its sub-blocks."""
      all_blocks.append(block.text_block.text)
      for sub_block in block.text_block.blocks:
        extract_text_recursive(sub_block)  # Recursive call for nested blocks

  extraction = ""

  print("|| Document Layout ||")
  blocks = document.document_layout.blocks
  for block in blocks:
    extract_text_recursive(block)

  print(''.join(all_blocks))
  return ''.join(all_blocks)
system_instruction = """
When processing document extractions, pay close attention to elements identified as images, particularly 
Tables and Figures.  

Tables typically contain structured data such as capability ratings, use-case weightings, overall product scores, 
and evaluation criteria with weightings. Prioritize extracting the specific numerical or categorical values associated 
with vendors, capabilities, and use cases from these tables.
Figures, including Magic Quadrant charts and use-case score graphics, provide a visual summary of vendor positioning or performance. Extract the relative positions of vendors or their scores as depicted in these graphics.

Also look for images that may depict User Interfaces (e.g., editor integrations, dashboards, chat interfaces, 
workflow builders) or System Diagrams (e.g., network layouts, data flows), as these can provide context on how 
capabilities are presented or implemented.  

While using your rag tool `retrieval` send a more extend but concise prompt based and all of the information 
above to extract no only text but image annotations.  

When responding to a query, integrate information derived from these image types alongside the textual content, 
ensuring direct support from the source material.
"""
#%%
import ast
from csv import writer
from csv import reader

def gen_ai(text):
    import vertexai
    from vertexai.language_models import TextGenerationModel

    vertexai.init(project="vtxdemos", location="us-central1")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
        """from the following bio what are the main attributes, use adjectives only,
    exepected response should be a python list:
    [attribute_1, attribute_2, ...],
    bio: 
    {text}""",
        **parameters
    )
    return response

#%%
with open("examples.csv", "r") as read_obj, open("examples_1.csv", "w", newline='') as write_obj:
    csv_reader = reader(read_obj)
    csv_writer = writer(write_obj)
    attributes = []
    
    for row in csv_reader:
        pred = gen_ai(row[0])
        print(ast.literal_eval(pred.text))
        attributes = [i for i in ast.literal_eval(pred.text) if i not in attributes]
        row.append(pred)
        csv_writer.writerow(row)
    
# %%
['american', 'contemporary', 'painter', 'visual', 'artist']

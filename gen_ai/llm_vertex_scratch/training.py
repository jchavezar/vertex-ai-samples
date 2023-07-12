#%%
PROJECT_ID="vtxdemos"
#%%
from kfp.dsl import component

@component(packages_to_install=["tensorflow","transformers", "datasets", "py7zr"])
def data_peprocess(source_uri: str, output_uri: str):
    from random import randint
    from itertools import chain
    from functools import partial
    from transformers import AutoTokenizer
    from datasets import load_dataset

    dataset = load_dataset("samsum")["train"]
    model_id = "bigscience/bloomz-7b1"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.model_max_length = 2048 # overwrite wrong value

    prompt_template = f"Summarize the chat dialogue:\n{{dialogue}}\n---\nSummary:\n{{summary}}{{eos_token}}"
    def template_dataset(sample):
        sample["text"] = prompt_template.format(dialogue=sample["dialogue"],
                                                summary=sample["summary"],
                                                eos_token=tokenizer.eos_token)
        return sample


    # apply prompt template per sample
    dataset = dataset.map(template_dataset, remove_columns=list(dataset.features))
    
    print(dataset[randint(0, len(dataset))]["text"])

    remainder = {"input_ids": [], "attention_mask": []}
    
    def chunk(sample, chunk_length=2048):
        # define global remainder variable to save remainder from batches to use in next batch
        global remainder
        # Concatenate all texts and add remainder from previous batch
        concatenated_examples = {k: list(chain(*sample[k])) for k in sample.keys()}
        print(concatenated_examples)
        concatenated_examples = {k: remainder[k] + concatenated_examples[k] for k in concatenated_examples.keys()}
        # get total number of tokens for batch
        batch_total_length = len(concatenated_examples[list(sample.keys())[0]])

        # get max number of chunks for batch
        if batch_total_length >= chunk_length:
            batch_chunk_length = (batch_total_length // chunk_length) * chunk_length

        # Split by chunks of max_len.
        result = {
            k: [t[i : i + chunk_length] for i in range(0, batch_chunk_length, chunk_length)]
            for k, t in concatenated_examples.items()
        }
        # add remainder to global variable for next batch
        remainder = {k: concatenated_examples[k][batch_chunk_length:] for k in concatenated_examples.keys()}
        # prepare labels
        result["labels"] = result["input_ids"].copy()
        return result


    # tokenize and chunk dataset
    lm_dataset = dataset.map(
        lambda sample: tokenizer(sample["text"]), batched=True, remove_columns=list(dataset.features)
    ).map(
        partial(chunk, chunk_length=2048),
        batched=True,
    )

    # Print total number of samples
    print(f"Total number of samples: {len(lm_dataset)}")
    print(source_uri.path)
    print(output_uri.path)
    

from kfp.dsl import pipeline


@pipeline(name="llm7b_lora")
def pipeline(
    source_uri: str
):
    preprocess_job = data_peprocess(
        source_uri=source_uri,
        output_uri="gs://vtxdemos-datasets-public/llm7b_lora"
    )

from kfp import compiler

compiler.Compiler().compile(
    pipeline_func=pipeline,
    package_path='llm7b_lora.yaml'
)

#%%
import google.cloud.aiplatform as aip

# Before initializing, make sure to set the GOOGLE_APPLICATION_CREDENTIALS
# environment variable to the path of your service account.
aip.init(
    project=PROJECT_ID,
    location="us-central1",
)

# Prepare the pipeline job
job = aip.PipelineJob(
    display_name="llm7b_lora",
    template_path="llm7b_lora.yaml",
    pipeline_root="gs://vtxdemos-tmp",
    parameter_values={
        'source_uri': "gs://vtxdemos-datasets-public"
    }
)

job.submit()
# %%

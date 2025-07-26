import pandas as pd

train_df = pd.DataFrame({'text': train_examples, 'labels': train_labels})
test_df = pd.DataFrame({'text': train_examples, 'labels': train_labels})

# %%
train_df.to_csv('train.csv', index=False)
test_df.to_csv('test.csv', index=False)
# %%



train_data, test_data = tfds.load(name="imdb_reviews", split=["train", "test"], 
                                  batch_size=-1, as_supervised=True)

train_examples, train_labels = tfds.as_numpy(train_data)
test_examples, test_labels = tfds.as_numpy(test_data)
# %%


train_examples_list = [i.decode('utf-8') for i in train_examples]
test_examples_list = [i.decode('utf-8') for i in test_examples]
# %%
import pandas as pd

train_df = pd.DataFrame({"text": train_examples_list, "labels": train_labels})
test_df = pd.DataFrame({"text": test_examples_list, "labels": test_labels})

# %%
train_df.to_gbq('vtxdemos.public.train_nlp', if_exists='replace')
# %%
test_df.to_gbq('vtxdemos.public.test_nlp', if_exists='replace')

#%%

from torchdata.datapipes.iter import IterableWrapper

dp = IterableWrapper(["gcs://vtxdemos-tmp/test.zip"]) \
        .open_files_by_fsspec(mode="rb") \
        .load_from_zip()
# Logic to process those archive files comes after
for path, filestream in dp:
    print(path, filestream)

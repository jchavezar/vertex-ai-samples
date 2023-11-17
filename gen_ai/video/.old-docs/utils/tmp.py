#%%
class A:
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)
 
x={"text":1}

test2=A(x)
# %%

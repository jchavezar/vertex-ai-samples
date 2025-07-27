#%%
import time
import tqdm
import numpy as np
import multiprocessing
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

#region Visualization
def plot_tasks(tasks):
    fig = plt.figure(figsize=(20,10))
    ax = fig.add_subplot()
    for task in tasks['timing']:
        ax.add_patch(
            Rectangle(
                (task[1][0], task[0]-.5),
                width = task[1][1] - task[1][0],
                height = 1,
                color = 'green'
            )
        )
    plt.xlim([0, tasks['timing_range'][1]-tasks['timing_range'][0]])
    plt.ylim([
        tasks['timing'][0][0]-0.5,
        tasks['timing'][-1][0]+0.5
    ])
    plt.xlabel("Time (seconds)")
    plt.ylabel("Tasks")
    plt.title(f"Timeline for Executing Tasks")
    plt.show()
#endregion

def local_task(b, n, d):
    task_begin = time.perf_counter()
    
    # do tasks locally: generate data and fit least-squares
    #b = [0.75, 1.88]
    #n = 50000
    #d = 1
    n = int(n)
    x = np.random.rand(n)*10
    y = b[0] + b[1] * x + np.random.normal(0, d, n)
    b_hat = np.linalg.lstsq(np.vstack([np.ones(len(x)), x]).T, y, rcond=None)[0]
    
    task_end = time.perf_counter()
    return task_begin, task_end


total_requests = 20
concur_requests = multiprocessing.cpu_count() - 1 # reserve a cpu for managing jobs...

begin = time.perf_counter()
# make of list of set (list) of inputs for each request.  Here its just the repeat parameter set.
calls = [[[0.75, 1.88], 5000000, 1, begin, i] for i in range(total_requests)]

# make a function that calls the local function, passes inputs
# if the local function only has a single input this is not really needed!
def call_local_task(inputs):
    process = multiprocessing.current_process().pid
    task = local_task(inputs[0], inputs[1], inputs[2])
    return (inputs[4], (task[0] - inputs[3], task[1] - inputs[3]), process)

# create a pool, map the list of input sets to the calling function.  Use tqdm to watch progress over input sets.
pool = multiprocessing.Pool(concur_requests)
timing = list(
    tqdm.tqdm(
        pool.imap(
            call_local_task,
            calls
        ),
        total = len(calls)
    )
)
pool.close()
pool.join()
end = time.perf_counter()
# %%
local_tasks = {'timing': timing, 'timing_range': (begin, end)}

# %%
plot_tasks(local_tasks)


# %%

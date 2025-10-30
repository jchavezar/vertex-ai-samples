#%%
from io import BytesIO
import pandas as pd
from markitdown import MarkItDown
import pandas as pd
import numpy as np

# --- 1. Setup ---
N_ROWS = 50
FILE_NAME = 'Synthetic_Chart_Data.xlsx'

# Set a seed for reproducibility (so you get the exact same numbers every time)
np.random.seed(42)

# --- 2. Data Generation with Good Distribution ---

# Unique Identifier for 50 rows
transaction_id = [f'TID{i:03d}' for i in range(1, N_ROWS + 1)]

# Sales Amount (Continuous, Normal Distribution for Bell Curve charts)
# Mean: 500, Standard Deviation: 150
sales_mean = 500
sales_std = 150
sales_amount = np.round(
    np.random.normal(loc=sales_mean, scale=sales_std, size=N_ROWS),
    2
)
sales_amount[sales_amount < 0] = 0 # Ensure no negative sales

# Units Sold (Discrete Count, Poisson Distribution for frequency charts)
# Lambda (mean): 10
units_sold = np.random.poisson(lam=10, size=N_ROWS)

# Region (Categorical, Skewed Distribution for unequal comparisons)
# Probabilities: East (40%), West (30%), North (20%), South (10%)
regions = np.random.choice(
    ['East', 'West', 'North', 'South'],
    size=N_ROWS,
    p=[0.40, 0.30, 0.20, 0.10]
)

# --- 3. Create DataFrame and Export ---
data = pd.DataFrame({
    'TransactionID': transaction_id,
    'SalesAmount': sales_amount,
    'UnitsSold': units_sold,
    'Region': regions
})

# EXPORT: This line creates the actual .xlsx file
# NOTE: You must have the 'openpyxl' library installed (`pip install openpyxl`)
try:
    data.to_excel(
        FILE_NAME,
        sheet_name='Chart_Data',
        index=False
    )
    print(f"✅ Data successfully saved to {FILE_NAME}")
except ImportError:
    print("❌ ERROR: Please install the required library: `pip install openpyxl`")
except Exception as e:
    print(f"An unexpected error occurred: {e}")


with open("Synthetic_Chart_Data.xlsx", "rb") as f:
    data = f.read()

decoded_data = BytesIO(data)

md = MarkItDown()

# Pass the file_name to help markitdown select the correct converter
result = md.convert(decoded_data)

print(result.text_content)
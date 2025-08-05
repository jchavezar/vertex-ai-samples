sql_query_prompt = """
### **Objective:**
Generate a SQL query for BigQuery.

### **Dataset_id.Table_id:**
`vtxdemos.demos_us.reviews_synthetic_data_1`

### **<Table.Schema>:**
*   `responseid`: (STRING) Unique identifier for the NPS response.
*   `nps_nps_group`: (STRING) NPS group (e.g., Promoter, Passive, Detractor).
*   `nps`: (INTEGER) NPS score as a string (e.g., '10', '6').
*   `company_name`: (STRING) Name of the company associated with the feedback.
*   `division`: (STRING) Division within the company (e.g., S&P Global Market Intelligence).
*   `consolidateregion`: (STRING) Consolidated geographical region (e.g., EMEA, LATAM, APAC). Convert 'NaN' or '(Blank)' from raw data to an empty string '' in the JSON.
*   `date_iso`: (DATE) Date of the feedback in 'YYYY-MM-DD' format to be compatible with BigQuery's DATE type. (DATA YEAR 2025)
*   `strategic_company`: (STRING) Indicates if the company is strategic. 'Yes' from raw data remains 'Yes'. Convert 'NaN' from raw data to an empty string '' in the JSON.
*   `nps_verbatim_combine`: (STRING) Combined verbatim feedback from the NPS response. Convert 'NaN' from raw data to an empty string '' in the JSON.
*   `mistake_applied`: (BOOLEAN) Indicates if a mistake was applied to this feedback. Convert 'Yes' from raw data to true, and 'NaN' to false in the JSON.

### **Synonyms and Variations:**

*   **company_name:**
    *   "Air b and b", "Air b&b", "airbnb" should all be treated as "Airbnb".
    *   "Google", "google llc", "Alphabet" should all be treated as "Google".
    *   "The Coca-Cola Company", "Coca-Cola", "coke" should all be treated as "Coca-Cola".
*   **consolidateregion:**
    *   "Europe, Middle East, and Africa", "emea" should all be treated as "EMEA".
    *   "Latin America", "latam" should all be treated as "LATAM".
    *   "Asia-Pacific", "apac" should all be treated as "APAC".
    *   "North America", "na" should all be treated as "North America".

### **Instructions:**

1.  From the user query, generate a `<sql_query>` that captures their intent, using the provided `<Dataset_id.Table_id>` and `<Table.Schema>`.
2.  Your generated SQL query must be syntactically correct for BigQuery.
3.  **Handle variations in `company_name` and `consolidateregion`**:
    *   When a user mentions a company or region, use the examples in the **Synonyms and Variations** section to map it to the standardized name in the database.
    *   For fuzzy matching of company and region names that might not be in the synonym list, use the `LOWER()` function and the `LIKE` operator (e.g., `LOWER(company_name) LIKE '%air b and b%'`).
4.  **Handle Ambiguity**:
    *   If a user's query is ambiguous and could refer to multiple distinct entities (e.g., "show me results for 'united'"), and you cannot infer the correct one from the context, you should return a query that includes all possible matches based on a `LIKE` comparison.
5.  Always aim to provide a single, executable SQL query.

### **Few-shot Examples:**

**Example 1:**
*   **User Query:** "Show me all the feedback for Air b and b in EMEA."
*   **<sql_query>:**
    ```sql
    SELECT *
    FROM `vtxdemos.demos_us.reviews_synthetic_data_1`
    WHERE LOWER(company_name) LIKE '%airbnb%'
      AND consolidateregion = 'EMEA'
    ```

**Example 2:**
*   **User Query:** "What is the average NPS score for Google in North America?"
*   **<sql_query>:**
    ```sql
    SELECT AVG(nps)
    FROM `vtxdemos.demos_us.reviews_synthetic_data_1`
    WHERE LOWER(company_name) LIKE '%google%'
      AND consolidateregion = 'North America'
    ```

**Example 3:**
*   **User Query:** "List all the promoters' feedback for Coca-Cola."
*   **<sql_query>:**
    ```sql
    SELECT nps_verbatim_combine
    FROM `vtxdemos.demos_us.reviews_synthetic_data_1`
    WHERE LOWER(company_name) LIKE '%coca-cola%'
      AND nps_nps_group = 'Promoter'
    ```
    
URL for SQL Query Syntaxis Validation: https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
"""
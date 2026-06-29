#%%
from google import genai
from google.genai import types
import base64
import os

def generate():
  client = genai.Client(
      vertexai=True,
  )

  msg1_document1 = types.Part.from_uri(
      file_uri="gs://vtxdemos-datasets-private/accenture/22379/96168, VACC, All Employees, Ed. 2-2024, 39.pdf",
      mime_type="application/pdf",
  )
  msg1_document2 = types.Part.from_uri(
      file_uri="gs://vtxdemos-datasets-private/accenture/22379/Medical Record.pdf",
      mime_type="application/pdf",
  )
  msg1_document3 = types.Part.from_uri(
      file_uri="gs://vtxdemos-datasets-private/accenture/22379/MR5.pdf",
      mime_type="application/pdf",
  )
  msg1_document4 = types.Part.from_uri(
      file_uri="gs://vtxdemos-datasets-private/accenture/22379/Medical Record_Discharge Summary.pdf",
      mime_type="application/pdf",
  )
  msg1_document5 = types.Part.from_uri(
      file_uri="gs://vtxdemos-datasets-private/accenture/22379/Medical Record_Doctor's Notes.pdf",
      mime_type="application/pdf",
  )
  msg1_document6 = types.Part.from_uri(
      file_uri="gs://vtxdemos-datasets-private/accenture/22379/Medical Record_Note from Provider.pdf",
      mime_type="application/pdf",
  )
  msg1_text1 = types.Part.from_text(text="""### PROMPT VERSION V4.5

### ROLE AND RESPONSIBILITIES:
- You are a medical insurance assessor with strong domain expertise in the insurance industry and Prudential Financial's business.
- Your task is to analyze various insurance claim-related documents to extract specific, benefit-level factual data and conduct an initial pre-assessment for policy exclusions.

----------------------------------------------------------------------------------------

### INPUT:
- Input as Attached Files:
 1. Medical Records
 2. Policy Certificate

- Input as JSON Data:
  1. INFORMATION_FROM_CLIENT_SYSTEM - Information from Client System: `[{\"KeyName\":\"RPA Intake Completion Date & Time\",\"KeyValue\":[\"05/15/2026 05:26:12\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claimant First Name\",\"KeyValue\":[\"Denise\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claimant Last Name\",\"KeyValue\":[\"Whildin\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Payment method (EFT/Check)\",\"KeyValue\":[\"Electronic Funds Transfer\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim Creation Date\",\"KeyValue\":[\"2/28/2026 9:35 AM\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim ID\",\"KeyValue\":[\"C-2024-664184\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Case ID\",\"KeyValue\":[\"4550\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Claim Type\",\"KeyValue\":[\"Follow Up\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Channel\",\"KeyValue\":[\"Web\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_First Notified Date\",\"KeyValue\":[\"3/2/2026\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Claimed By\",\"KeyValue\":[\"Denise Whildin\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Relationship\",\"KeyValue\":[\"Self\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Filename of the Document\",\"KeyValue\":[\"Claim Forms, Medical Records, Medical Records, Medical Records, Medical Records, Medical Records, Medical Records, Medical Records, Medical Records, Medical Records, Medical Records, Partial Claim Approved, Medical Records, Medical Records, Add'l Information Needed - Follow-up 2, PXL_20260304_135830398.jpg, PXL_20260304_135837860.jpg, PXL_20260304_135852380.jpg, PXL_20260304_135935117.jpg, PXL_20260304_135830398.jpg, PXL_20260304_135935117.jpg, PXL_20260304_135852380.jpg, PXL_20260304_135837860.jpg, PXL_20260304_135830398.jpg, Add'l Information Needed\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Additional Document Received Date\",\"KeyValue\":[\"5/15/2026, 5/1/2026, 5/1/2026, 5/1/2026, 5/1/2026, 5/1/2026, 5/1/2026, 5/1/2026, 5/1/2026, 5/1/2026, 5/1/2026, 4/8/2026, 4/3/2026, 4/1/2026, 3/30/2026, 3/4/2026, 3/4/2026, 3/4/2026, 3/4/2026, 3/4/2026, 3/4/2026, 3/4/2026, 3/4/2026, 3/4/2026, 3/4/2026\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Assigned To\",\"KeyValue\":[\"marjo.kean.balois@prudential.com\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Claimant Address\",\"KeyValue\":[\"23 Heron AvenuePennsville, New Jersey 08070United States\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Claimant Email ID\",\"KeyValue\":[\"dwhildin@holtlogistics.com\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Claimant Phone Number\",\"KeyValue\":[\"(856) 678-0778\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Claim Status\",\"KeyValue\":[\"Open\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Claimant DOB\",\"KeyValue\":[\"3/2/1961\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Group Name \",\"KeyValue\":[\"Holt Logistics Corp.\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Group ID \",\"KeyValue\":[\"96168\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Associate Group\",\"KeyValue\":[\"Holt Logistics Corp.\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Escalated Group\",\"KeyValue\":[\"Holt Logistics Corp.\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Claim_Resident State\",\"KeyValue\":[\"New Jersey\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Covered Person\",\"KeyValue\":[\"Denise Whildin\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Situs State\",\"KeyValue\":[\"New Jersey\"],\"RowNumber\":\"0\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Emergency Room\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-687505\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Cancelled\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Documentation doesn't support Claim\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"1\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Medical appliance - Crutches\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-687506\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Denied\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Documentation doesn't support Claim\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"2\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Urgent Care\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-687507\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Documentation doesn't support Claim\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"3\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Walking boot\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-687508\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Documentation doesn't support Claim\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"4\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Physical Therapy\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-687509\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Documentation doesn't support Claim\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"5\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Physician Follow-Up Visits\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-687510\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"6\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"X-Ray Benefit\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-687511\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"7\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Closed Reduction - Fracture, foot except toes\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-689671\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"8\"},{\"KeyName\":\"Benefit_For Accident_ Date of Accident\",\"KeyValue\":[\"2/1/2026\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Benefit_Admission Date\",\"KeyValue\":[\"2/2/2026\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Benefit_Benefit ID\",\"KeyValue\":[\"BC-2026-1842471\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Benefit_Benefit Status\",\"KeyValue\":[\"Completed\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Coverage_Coverage Name\",\"KeyValue\":[\"Vocational Therapy\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Coverage_Coverage ID\",\"KeyValue\":[\"CC-2026-689672\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Coverage_Coverage Status\",\"KeyValue\":[\"Cancelled\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Coverage_Coverage Status Reason\",\"KeyValue\":[\"Approved\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Benefit_Plan Type\",\"KeyValue\":[\"ACC-TB Medium - Group (Composite Rate)\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Benefit_Approved Benefit Amount\",\"KeyValue\":[\"$0.00\"],\"RowNumber\":\"9\"},{\"KeyName\":\"Benefit_Eligibility Status\",\"KeyValue\":[\"Eligible\"],\"RowNumber\":\"9\"}]` 
 --------------------------------------------------------------------------------------

  2. CLAIM_FORM_EXTRACTED_FIELDS - Custom extracted fields from Claim Form: `[{\"Accident Benefit Selection/hospital Benefit /Selected Condition\":[\"N/A\"]},{\"Accident Description\":[\"Accident: VACCI Hospital Indemnity: HIP1 Critical Illness: CR1\"]},{\"CaseID Dummy\":[\"QB-\"]},{\"Claim Submission Date\":[\"04/25/2024\"]},{\"Diagnosis Date/Date of Diagnosis\":[\"03/11/2024\"]},{\"Selected Condition\":[\"Autism Hospital Admissions\"]},{\"What Happened?\":[\"Hospitalization due to Illness / Condition\"]}]`  
 --------------------------------------------------------------------------------------
  
  3. BENEFIT_TYPES - all applicable benefit types :`[{\"KeyName\":\"Benefit_Benefit Type\",\"KeyValue\":[\"ATB\"]}]`

----------------------------------------------------------------------------------------

### INSTRUCTION:
- Generate Output STRICTLY as defined in OUTPUT FORMAT.
- Do not include any explanation or introductory text before or after in the JSON.
- Task Overview:
 - Identify Applicable Benefit Types: From BENEFIT_TYPES, identify all applicable benefit types for the claim. Normalize these to: CI (Critical Illness), HIP (Hospital Indemnity), ATB (Accidental Benefit). Include each short form only once.
 - Process Each Benefit Type: For each identified benefit type, create a separate JSON object.
 - Extract BenefitSpecificData: Extract the specific fields relevant to that benefit type, adhering to the \"Hierarchy of Truth\" and \"Date Formatting\" rules.
 - Perform Policy Exclusion Check: Review the Policy Certificate against Medical Records for any applicable exclusions.

----------------------------------------------------------------------------------------

### BUSINESS RULES:
RULE 1: Hierarchy of Truth (Precedence Rule) for `BenefitSpecificData` fields <<
 - In case of conflicted information, you MUST prioritize sources in this order:
 - Medical Record Excerpt (Primary Source - The \"Medical Truth\")
 - Claim Form (`CLAIM_FORM_EXTRACTED_FIELDS`)
 - Information from Client System (`INFORMATION_FROM_CLIENT_SYSTEM`)
 >>

RULE 2: Date Formatting: <<
 - Format all dates in the final output as MM/DD/YYYY.
 >>

RULE 3: Date of Service (DOS) Handling for Extraction <<
 - Extract from Medical Records first.
 - Fallback to Claim Form(`CLAIM_FORM_EXTRACTED_FIELDS`) if missing in records.
 - Final fallback to Client System(`INFORMATION_FROM_CLIENT_SYSTEM`).
 >>

RULE 4: `BenefitSpecificData` Extraction <<
 - Only extract the fields listed below for the respective benefit type.
 - If a specific field's value is missing after applying the Hierarchy of Truth, return `\"\"` (empty string) for that field.
 - Fields by Benefit Type:
 - `HIP`:
 - `\"Admission Date\"` (MM/DD/YYYY)
 - `\"Discharge Date\"` (MM/DD/YYYY)
 - `\"Reason for Hospitalization\"` (Text)
 - `ATB`:
 - `\"Date of Accident\"` (MM/DD/YYYY)
 - \"Accident Details\" (One-line summary: Nature, Mechanism, Injury Type)
 - `CI`:
 - `\"Diagnosis Date\"` (MM/DD/YYYY)
 - `\"Name of Condition Illness\"` (description e.g., `\"Stroke\"`, `\"Cancer\"`)
 >>

RULE 5: `Policy Exclusion Check` Logic <<
 - Step 1: Identify Applicable Exclusion Sections in Policy Certificate.
 - Primary Search: First, search for a section explicitly titled \"Exclusions\", \"General Exclusions\", \"What is Not Covered\", or similar, within the Policy Certificate. This is the primary source for all benefit types.
 - Secondary Search (CI Only):If, and ONLY IF, no such general 'Exclusions' section is found in the Policy Certificate, then for Critical Illness (CI) benefits, specifically search only within the section titled \"CRITICAL ILLNESSES NOT COVERED\" (e.g., 'B. CRITICAL ILLNESSES NOT COVERED') located under the 'CRITICAL ILLNESS COVERAGE' part of the Policy Certificate.
  - Do not look into any other sections or any other part of the 'CRITICAL ILLNESS COVERAGE' section for exclusions. 
  - This section is considered only as a fallback for CI if the primary 'Exclusions' section is absent.
 - Strict Limitation Information appearing in any other section* of the Policy Certificate, regardless of its content (e.g., within benefit definitions, eligibility criteria, or general information), must NOT be treated as an exclusion clause for the purpose of this check. Only clauses found directly within the explicitly identified primary or secondary exclusion sections are valid.

 - Step 2: Cross-Reference with Medical Records.
  - For each identified exclusion clause from Step 1, check the `Medical Records` for direct, unambiguous, and reliable evidence that specifically and clearly triggers that exclusion clause. 
  - Do not infer or assume. 
  - The medical record evidence must directly support the condition described in the exclusion.

 - Step 3: Determine Outcome.
 - `Policy Exclusion Applicable`:
 - Report \"Yes\" ONLY if an exclusion clause was identified in Step 1 AND there is clear, direct, and unambiguous evidence in the `Medical Records` (from Step 2) that triggers that specific clause.
 - Otherwise, report \"No\".
 - `Exclusion Clause Description`:
 - If `Policy Exclusion Applicable` is \"Yes\", provide a concise 2-4 word summary of the key concept of the triggered exclusion (e.g., \"Pre-existing Condition\", \"Self-Inflicted Injury\", \"Alcohol/Drug Abuse\").
 - If `Policy Exclusion Applicable` is \"No\", use \"NA\".
 - If the `Policy Certificate` for the policy overall is missing or cannot be identified, use \"Not Determined\".
 - `Policy Exclusion Result`:
 - If `Policy Exclusion Applicable` is \"Yes\": State the specific reason why the exclusion is applicable, and provide a direct quote from the Policy Certificate (citing the relevant section and Page/Section) and a direct quote from `Medical Records` (with Page/Section) supporting the trigger.
 - If `Policy Exclusion Applicable` is \"No\": `\"No relevant policy exclusion found.\"`
 - If the `Policy Certificate` document is not present or identifiable for this claim: `\"Policy document not present.\"`
 >>

----------------------------------------------------------------------------------------

### OUTPUT FORMAT:
```json
[
 {
 \"Benefit Type\": \"<CI | HIP | ATB>\",
 \"BenefitSpecificData\": {
 // Only the fields relevant to the benefit type and extracted in this step.
 // Use \"\" if value is missing.
 // Date fields in MM/DD/YYYY format.
 // Example for HIP:
 // \"Admission Date\": \"MM/DD/YYYY\",
 // \"Discharge Date\": \"MM/DD/YYYY\",
 // \"Reason for Hospitalization\": \"Text describing reason\"
 },
 \"Policy Exclusion Check\": {
 \"Policy Exclusion Applicable\": \"<Yes | No>\",
 \"Exclusion Clause Description\": \"<Clause Name | NA>\",
 \"Policy Exclusion Result\": \"<Reason for applicability with quotes | No relevant policy exclusion found. | Policy document not present.>\"
 }
 }
 ]""")

  model = "gemini-2.5-flash"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_document1,
        msg1_document2,
        msg1_document3,
        msg1_document4,
        msg1_document5,
        msg1_document6,
        msg1_text1
      ]
    ),
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 1,
    seed = 0,
    max_output_tokens = 65535,
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    thinking_config=types.ThinkingConfig(
      thinking_budget=-1,
    ),
  )

  import time
  start_time = time.time()
  first_chunk_time = None

  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    if first_chunk_time is None:
        first_chunk_time = time.time()
    print(chunk.text, end="")

  end_time = time.time()
  print("\n\n=== LATENCY METRICS ===")
  if first_chunk_time:
      print(f"Time to First Chunk (TTFT): {first_chunk_time - start_time:.4f} s")
  print("#"*80)
  print(f"Total Latency: {end_time - start_time:.4f} s")

generate()
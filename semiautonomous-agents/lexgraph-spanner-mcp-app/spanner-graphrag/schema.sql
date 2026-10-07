-- ============================================================================
-- LEXGRAPH LEGAL CONTEXT ENGINE — CLOUD SPANNER GRAPH + VECTOR + FTS DDL
-- Instance: lexgraph-legal-spanner | Database: lexgraph-legal-context
-- Embeddings: Vertex AI gemini-embedding-2 (ARRAY<FLOAT64>, 3,072 dimensions)
-- ============================================================================

-- 1. Lawyers (Identity & Practice Group Nodes)
CREATE TABLE Lawyers (
    lawyer_id STRING(64) NOT NULL,
    email STRING(128) NOT NULL,
    full_name STRING(128) NOT NULL,
    role_title STRING(128),
    practice_group STRING(64),
    office STRING(64),
) PRIMARY KEY (lawyer_id);

-- 2. Matters (Deal / Engagement Nodes)
CREATE TABLE Matters (
    matter_id STRING(64) NOT NULL,
    matter_name STRING(256) NOT NULL,
    client_name STRING(256),
    practice_area STRING(64),
    deal_value_usd FLOAT64,
    status STRING(64),
) PRIMARY KEY (matter_id);

-- 3. Documents (iManage DMS Contract Metadata Nodes)
CREATE TABLE Documents (
    doc_id STRING(64) NOT NULL,
    matter_id STRING(64) NOT NULL,
    title STRING(512) NOT NULL,
    doc_type STRING(64),
    dms_version STRING(64),
    counsel_firm STRING(128),
    governing_law STRING(64),
    execution_date STRING(32),
) PRIMARY KEY (doc_id);

-- 4. Clauses (Hybrid Vector 3,072-dim + Full-Text Search Tokenlist Nodes)
CREATE TABLE Clauses (
    clause_id STRING(64) NOT NULL,
    doc_id STRING(64) NOT NULL,
    matter_id STRING(64) NOT NULL,
    clause_type STRING(128),
    section_ref STRING(128),
    page_number INT64,
    cap_pct STRING(64),
    basket_type STRING(128),
    survival_months STRING(64),
    qualifiers STRING(256),
    summary_text STRING(MAX),
    verbatim_quote STRING(MAX),
    embedding ARRAY<FLOAT64>,
    fts_tokens TOKENLIST AS (TOKENIZE_FULLTEXT( summary_text || ' ' || verbatim_quote || ' ' || qualifiers )) HIDDEN,
) PRIMARY KEY (clause_id);

CREATE SEARCH INDEX ClausesFtsIdx ON Clauses(fts_tokens);

-- 5. UnfiledEmails (Partner Silo Correspondence Governed by TeammateGrants)
CREATE TABLE UnfiledEmails (
    email_id STRING(64) NOT NULL,
    matter_id STRING(64) NOT NULL,
    owner_lawyer_id STRING(64) NOT NULL,
    sender_email STRING(128),
    subject STRING(512),
    sent_at STRING(64),
    body_excerpt STRING(MAX),
    embedding ARRAY<FLOAT64>,
) PRIMARY KEY (email_id);

-- 6. Graph Edge Tables (Intapp Ethical Walls, Authorizations, Citations & 30d Grants)
CREATE TABLE LawyerAuthorizedMatter (
    lawyer_id STRING(64) NOT NULL,
    matter_id STRING(64) NOT NULL,
    clearance_source STRING(64),
    granted_at STRING(64),
) PRIMARY KEY (lawyer_id, matter_id);

CREATE TABLE EthicalWallBlocks (
    lawyer_id STRING(64) NOT NULL,
    matter_id STRING(64) NOT NULL,
    wall_id STRING(64) NOT NULL,
    reason STRING(256),
) PRIMARY KEY (lawyer_id, matter_id);

CREATE TABLE ClauseNegotiatedBy (
    clause_id STRING(64) NOT NULL,
    counsel_name STRING(128) NOT NULL,
    position_taken STRING(256),
) PRIMARY KEY (clause_id, counsel_name);

CREATE TABLE TeammateGrants (
    grant_id STRING(64) NOT NULL,
    email_id STRING(64) NOT NULL,
    owner_lawyer_id STRING(64) NOT NULL,
    grantee_lawyer_id STRING(64) NOT NULL,
    matter_id STRING(64) NOT NULL,
    granted_at STRING(64),
    expires_at STRING(64),
    status STRING(64),
) PRIMARY KEY (grant_id);

-- 7. Property Graph Definition (ISO/IEC 9075-16 GQL)
CREATE OR REPLACE PROPERTY GRAPH LexGraphLegalGraph
  NODE TABLES (
    Lawyers,
    Matters,
    Documents,
    Clauses,
    UnfiledEmails
  )
  EDGE TABLES (
    LawyerAuthorizedMatter
      SOURCE KEY (lawyer_id) REFERENCES Lawyers (lawyer_id)
      DESTINATION KEY (matter_id) REFERENCES Matters (matter_id)
      LABEL AUTHORIZED_FOR,
    EthicalWallBlocks
      SOURCE KEY (lawyer_id) REFERENCES Lawyers (lawyer_id)
      DESTINATION KEY (matter_id) REFERENCES Matters (matter_id)
      LABEL ETHICAL_WALL_BLOCK,
    TeammateGrants
      SOURCE KEY (owner_lawyer_id) REFERENCES Lawyers (lawyer_id)
      DESTINATION KEY (grantee_lawyer_id) REFERENCES Lawyers (lawyer_id)
      LABEL TEAMMATE_GRANT
  );

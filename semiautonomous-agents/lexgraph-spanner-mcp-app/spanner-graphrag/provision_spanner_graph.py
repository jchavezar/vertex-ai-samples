import subprocess
import urllib.request
import urllib.error
import json
import time

PROJECT_ID = "vtxdemos"
INSTANCE_ID = "lexgraph-legal-spanner"
DB_ID = "lexgraph-legal-context"

def get_headers():
    token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID
    }

DDL_STATEMENTS = [
    """CREATE TABLE Lawyers (
        lawyer_id STRING(64) NOT NULL,
        full_name STRING(128) NOT NULL,
        email STRING(128) NOT NULL,
        title STRING(64),
        practice_group STRING(64),
        office STRING(64)
    ) PRIMARY KEY (lawyer_id)""",

    """CREATE TABLE Clients (
        client_id STRING(64) NOT NULL,
        client_name STRING(128) NOT NULL,
        industry STRING(64),
        tier STRING(32)
    ) PRIMARY KEY (client_id)""",

    """CREATE TABLE Matters (
        matter_id STRING(64) NOT NULL,
        matter_name STRING(256) NOT NULL,
        client_id STRING(64) NOT NULL,
        practice_area STRING(64),
        status STRING(32),
        lead_partner_id STRING(64),
        deal_value_usd FLOAT64
    ) PRIMARY KEY (matter_id)""",

    """CREATE TABLE Documents (
        doc_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        title STRING(256) NOT NULL,
        doc_type STRING(64),
        counsel_firm STRING(128),
        governing_law STRING(64),
        execution_date STRING(32),
        pdf_filename STRING(256),
        page_count INT64,
        dms_version STRING(32)
    ) PRIMARY KEY (doc_id)""",

    """CREATE TABLE DocumentChunks (
        chunk_id STRING(64) NOT NULL,
        doc_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        section_ref STRING(128),
        page_number INT64,
        chunk_text STRING(MAX),
        bbox_json STRING(MAX),
        embedding ARRAY<FLOAT32>(vector_length=>3072),
        content_tokens TOKENLIST AS (TOKENIZE_FULLTEXT(chunk_text)) HIDDEN
    ) PRIMARY KEY (chunk_id)""",

    """CREATE TABLE Clauses (
        clause_id STRING(64) NOT NULL,
        doc_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        clause_type STRING(64) NOT NULL,
        section_ref STRING(128),
        page_number INT64,
        cap_pct STRING(64),
        basket_type STRING(128),
        survival_months STRING(64),
        qualifiers STRING(256),
        summary_text STRING(MAX),
        verbatim_quote STRING(MAX),
        counsel_firm STRING(128),
        governing_law STRING(64),
        bbox_json STRING(MAX),
        embedding ARRAY<FLOAT32>(vector_length=>3072),
        clause_tokens TOKENLIST AS (TOKENIZE_FULLTEXT(verbatim_quote)) HIDDEN
    ) PRIMARY KEY (clause_id)""",

    """CREATE TABLE Emails (
        email_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        sender_lawyer_id STRING(64) NOT NULL,
        recipient_lawyer_id STRING(64) NOT NULL,
        subject_line STRING(512) NOT NULL,
        body_text STRING(MAX),
        sent_timestamp STRING(64),
        visibility_state STRING(32),
        has_attachment BOOL,
        attachment_doc_id STRING(64)
    ) PRIMARY KEY (email_id)""",

    """CREATE TABLE WorkedOn (
        lawyer_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        role STRING(64),
        hours_logged FLOAT64
    ) PRIMARY KEY (lawyer_id, matter_id)""",

    """CREATE TABLE BelongsToMatter (
        doc_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        filing_type STRING(64)
    ) PRIMARY KEY (doc_id, matter_id)""",

    """CREATE TABLE ContainsClause (
        doc_id STRING(64) NOT NULL,
        clause_id STRING(64) NOT NULL,
        section_ref STRING(128)
    ) PRIMARY KEY (doc_id, clause_id)""",

    """CREATE TABLE CitesPrecedent (
        source_doc_id STRING(64) NOT NULL,
        target_doc_id STRING(64) NOT NULL,
        citation_reason STRING(256),
        similarity_score FLOAT64
    ) PRIMARY KEY (source_doc_id, target_doc_id)""",

    """CREATE TABLE IntappWalls (
        wall_id STRING(64) NOT NULL,
        lawyer_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        rule_type STRING(32) NOT NULL,
        reason STRING(256),
        enforced_at STRING(64)
    ) PRIMARY KEY (wall_id)""",

    """CREATE TABLE TeammateGrants (
        grant_id STRING(64) NOT NULL,
        email_id STRING(64) NOT NULL,
        owner_lawyer_id STRING(64) NOT NULL,
        grantee_lawyer_id STRING(64) NOT NULL,
        matter_id STRING(64) NOT NULL,
        granted_at STRING(64),
        expires_at STRING(64),
        status STRING(32)
    ) PRIMARY KEY (grant_id)""",

    """CREATE SEARCH INDEX ChunkFtsIndex ON DocumentChunks(content_tokens)""",
    """CREATE SEARCH INDEX ClauseFtsIndex ON Clauses(clause_tokens)""",

    """CREATE OR REPLACE PROPERTY GRAPH LexGraphLegalGraph
      NODE TABLES (
        Lawyers KEY (lawyer_id) LABEL Lawyer PROPERTIES (lawyer_id, full_name, email, title, practice_group, office),
        Clients KEY (client_id) LABEL Client PROPERTIES (client_id, client_name, industry, tier),
        Matters KEY (matter_id) LABEL Matter PROPERTIES (matter_id, matter_name, client_id, practice_area, status, lead_partner_id, deal_value_usd),
        Documents KEY (doc_id) LABEL Document PROPERTIES (doc_id, matter_id, title, doc_type, counsel_firm, governing_law, execution_date, pdf_filename, page_count, dms_version),
        Clauses KEY (clause_id) LABEL Clause PROPERTIES (clause_id, doc_id, matter_id, clause_type, section_ref, page_number, cap_pct, basket_type, survival_months, qualifiers, summary_text, verbatim_quote, counsel_firm, governing_law),
        Emails KEY (email_id) LABEL EmailMessage PROPERTIES (email_id, matter_id, sender_lawyer_id, recipient_lawyer_id, subject_line, body_text, sent_timestamp, visibility_state, has_attachment, attachment_doc_id)
      )
      EDGE TABLES (
        WorkedOn KEY (lawyer_id, matter_id)
          SOURCE KEY (lawyer_id) REFERENCES Lawyers (lawyer_id)
          DESTINATION KEY (matter_id) REFERENCES Matters (matter_id)
          LABEL WORKED_ON PROPERTIES (lawyer_id, matter_id, role, hours_logged),
        BelongsToMatter KEY (doc_id, matter_id)
          SOURCE KEY (doc_id) REFERENCES Documents (doc_id)
          DESTINATION KEY (matter_id) REFERENCES Matters (matter_id)
          LABEL BELONGS_TO_MATTER PROPERTIES (doc_id, matter_id, filing_type),
        ContainsClause KEY (doc_id, clause_id)
          SOURCE KEY (doc_id) REFERENCES Documents (doc_id)
          DESTINATION KEY (clause_id) REFERENCES Clauses (clause_id)
          LABEL CONTAINS_CLAUSE PROPERTIES (doc_id, clause_id, section_ref),
        CitesPrecedent KEY (source_doc_id, target_doc_id)
          SOURCE KEY (source_doc_id) REFERENCES Documents (doc_id)
          DESTINATION KEY (target_doc_id) REFERENCES Documents (doc_id)
          LABEL CITES_PRECEDENT PROPERTIES (source_doc_id, target_doc_id, citation_reason, similarity_score),
        IntappWalls KEY (wall_id)
          SOURCE KEY (lawyer_id) REFERENCES Lawyers (lawyer_id)
          DESTINATION KEY (matter_id) REFERENCES Matters (matter_id)
          LABEL INTAPP_WALL PROPERTIES (wall_id, lawyer_id, matter_id, rule_type, reason, enforced_at),
        TeammateGrants KEY (grant_id)
          SOURCE KEY (grantee_lawyer_id) REFERENCES Lawyers (lawyer_id)
          DESTINATION KEY (email_id) REFERENCES Emails (email_id)
          LABEL TEAMMATE_GRANT PROPERTIES (grant_id, email_id, owner_lawyer_id, grantee_lawyer_id, matter_id, granted_at, expires_at, status)
      )"""
]

def create_database():
    url = f"https://spanner.googleapis.com/v1/projects/{PROJECT_ID}/instances/{INSTANCE_ID}/databases"
    body = {
        "createStatement": f"CREATE DATABASE `{DB_ID}`",
        "extraStatements": DDL_STATEMENTS
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=get_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            op = json.loads(resp.read().decode())
            print("CREATE DB OP STARTED:", op.get("name"))
            op_name = op.get("name")
            while True:
                time.sleep(3)
                op_req = urllib.request.Request(f"https://spanner.googleapis.com/v1/{op_name}", headers=get_headers())
                with urllib.request.urlopen(op_req, timeout=30) as op_resp:
                    op_state = json.loads(op_resp.read().decode())
                    if op_state.get("done"):
                        if "error" in op_state:
                            print("DDL ERROR:", json.dumps(op_state["error"], indent=2))
                        else:
                            print("DATABASE & PROPERTY GRAPH CREATED SUCCESSFULLY!")
                        break
                    else:
                        print("Waiting for Spanner DDL operation to complete...")
    except urllib.error.HTTPError as e:
        print("HTTP ERROR:", e.code, e.read().decode())

if __name__ == "__main__":
    create_database()

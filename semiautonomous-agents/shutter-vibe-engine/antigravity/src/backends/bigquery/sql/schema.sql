-- BigQuery schema for the cost-optimized search path.
--
-- One row per indexed segment. We keep the table thin: vector + filter columns
-- only. Rich metadata (caption, GCS URIs, license, contributor) stays in
-- Firestore — same hydration step as the Vector Search path.
--
-- Run once:
--   bq --project_id=vtxdemos --location=us-central1 mk -d envato_vibe
--   bq --project_id=vtxdemos query --nouse_legacy_sql < schema.sql

CREATE TABLE IF NOT EXISTS `vtxdemos.envato_vibe.segments` (
  datapoint_id   STRING NOT NULL,
  modality       STRING,           -- photo | video | audio | sfx | graphic
  kind           STRING,           -- photo | video | music | sfx | graphic
  tempo_bucket   STRING,           -- slow | medium | fast (audio only)
  length_bucket  STRING,           -- short | medium | long
  embedding      ARRAY<FLOAT64>,   -- 3072-d, gemini-embedding-2-preview
  ingest_ts      TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY modality;
-- CLUSTER BY modality lets the planner skip non-matching blocks when the query
-- has WHERE modality = '...' — keeps brute-force scan cost minimal.

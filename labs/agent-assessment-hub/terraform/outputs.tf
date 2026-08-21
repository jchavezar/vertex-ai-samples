output "cloud_run_url" {
  description = "The deployed Cloud Run service URL"
  value       = google_cloud_run_v2_service.agent_service.uri
}

output "secret_manager_id" {
  description = "Secret Manager secret resource ID"
  value       = google_secret_manager_secret.agent_api_secret.id
}

prepare-images:
		bash build_docker_images/script.sh
training-pipeline:
		PYTHONPATH=. && \
		python training/pipeline.py && \
		python utils/tools/trigger_pipeline.py \
		--config_path training/config.yaml \
		--project ${PROJECT_ID}
    @classmethod
    def create(
        cls,
        reasoning_engine: Union[Queryable, OperationRegistrable],
        *,
        requirements: Optional[Union[str, Sequence[str]]] = None,
        reasoning_engine_name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        gcs_dir_name: str = _DEFAULT_GCS_DIR_NAME,
        sys_version: Optional[str] = None,
        extra_packages: Optional[Sequence[str]] = None,
    ) -> "ReasoningEngine":
        """Creates a new ReasoningEngine.

        The Reasoning Engine will be an instance of the `reasoning_engine` that
        was passed in, running remotely on Vertex AI.

        Sample ``src_dir`` contents (e.g. ``./user_src_dir``):

        .. code-block:: python

            user_src_dir/
            |-- main.py
            |-- requirements.txt
            |-- user_code/
            |   |-- utils.py
            |   |-- ...
            |-- ...

        To build a Reasoning Engine:

        .. code-block:: python

            remote_app = ReasoningEngine.create(
                local_app,
                requirements=[
                    # I.e. the PyPI dependencies listed in requirements.txt
                    "google-cloud-aiplatform==1.25.0",
                    "langchain==0.0.242",
                    ...
                ],
                extra_packages=[
                    "./user_src_dir/main.py", # a single file
                    "./user_src_dir/user_code", # a directory
                    ...
                ],
            )

        Args:
            reasoning_engine (ReasoningEngineInterface):
                Required. The Reasoning Engine to be created.
            requirements (Union[str, Sequence[str]]):
                Optional. The set of PyPI dependencies needed. It can either be
                the path to a single file (requirements.txt), or an ordered list
                of strings corresponding to each line of the requirements file.
            reasoning_engine_name (str):
                Optional. A fully-qualified resource name or ID such as
                "projects/123/locations/us-central1/reasoningEngines/456" or
                "456" when project and location are initialized or passed. If
                specifying the ID, it should be 4-63 characters. Valid
                characters are lowercase letters, numbers and hyphens ("-"),
                and it should start with a number or a lower-case letter. If not
                provided, Vertex AI will generate a value for this ID.
            display_name (str):
                Optional. The user-defined name of the Reasoning Engine.
                The name can be up to 128 characters long and can comprise any
                UTF-8 character.
            description (str):
                Optional. The description of the Reasoning Engine.
            gcs_dir_name (CreateReasoningEngineOptions):
                Optional. The GCS bucket directory under `staging_bucket` to
                use for staging the artifacts needed.
            sys_version (str):
                Optional. The Python system version used. Currently supports any
                of "3.9", "3.10", "3.11", "3.12", "3.13". If not specified,
                it defaults to the "{major}.{minor}" attributes of
                sys.version_info.
            extra_packages (Sequence[str]):
                Optional. The set of extra user-provided packages (if any).

        Returns:
            ReasoningEngine: The Reasoning Engine that was created.

        Raises:
            ValueError: If `sys.version` is not supported by ReasoningEngine.
            ValueError: If the `project` was not set using `vertexai.init`.
            ValueError: If the `location` was not set using `vertexai.init`.
            ValueError: If the `staging_bucket` was not set using vertexai.init.
            ValueError: If the `staging_bucket` does not start with "gs://".
            FileNotFoundError: If `extra_packages` includes a file or directory
            that does not exist.
            IOError: If requirements is a string that corresponds to a
            nonexistent file.
        """
        if not sys_version:
            sys_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        _validate_sys_version_or_raise(sys_version)
        reasoning_engine = _validate_reasoning_engine_or_raise(reasoning_engine)
        requirements = _validate_requirements_or_raise(requirements)
        extra_packages = _validate_extra_packages_or_raise(extra_packages)

        if reasoning_engine_name:
            _LOGGER.warning(
                "ReasoningEngine does not support user-defined resource IDs at "
                f"the moment. Therefore {reasoning_engine_name=} would be "
                "ignored and a random ID will be generated instead."
            )
        sdk_resource = cls.__new__(cls)
        base.VertexAiResourceNounWithFutureManager.__init__(
            sdk_resource,
            resource_name=reasoning_engine_name,
        )
        staging_bucket = initializer.global_config.staging_bucket
        _validate_staging_bucket_or_raise(staging_bucket)
        # Prepares the Reasoning Engine for creation in Vertex AI.
        # This involves packaging and uploading the artifacts for
        # reasoning_engine, requirements and extra_packages to
        # `staging_bucket/gcs_dir_name`.
        _prepare(
            reasoning_engine=reasoning_engine,
            requirements=requirements,
            project=sdk_resource.project,
            location=sdk_resource.location,
            staging_bucket=staging_bucket,
            gcs_dir_name=gcs_dir_name,
            extra_packages=extra_packages,
        )
        # Update the package spec.
        package_spec = aip_types.ReasoningEngineSpec.PackageSpec(
            python_version=sys_version,
            pickle_object_gcs_uri="{}/{}/{}".format(
                staging_bucket,
                gcs_dir_name,
                _BLOB_FILENAME,
            ),
        )
        if extra_packages:
            package_spec.dependency_files_gcs_uri = "{}/{}/{}".format(
                staging_bucket,
                gcs_dir_name,
                _EXTRA_PACKAGES_FILE,
            )
        if requirements:
            package_spec.requirements_gcs_uri = "{}/{}/{}".format(
                staging_bucket,
                gcs_dir_name,
                _REQUIREMENTS_FILE,
            )
        reasoning_engine_spec = aip_types.ReasoningEngineSpec(
            package_spec=package_spec,
        )
        class_methods_spec = _generate_class_methods_spec_or_raise(
            reasoning_engine, _get_registered_operations(reasoning_engine)
        )
        reasoning_engine_spec.class_methods.extend(class_methods_spec)
        operation_future = sdk_resource.api_client.create_reasoning_engine(
            parent=initializer.global_config.common_location_path(
                project=sdk_resource.project, location=sdk_resource.location
            ),
            reasoning_engine=aip_types.ReasoningEngine(
                name=reasoning_engine_name,
                display_name=display_name,
                description=description,
                spec=reasoning_engine_spec,
            ),
        )
        _LOGGER.log_create_with_lro(cls, operation_future)
        created_resource = operation_future.result()
        _LOGGER.log_create_complete(
            cls,
            created_resource,
            cls._resource_noun,
            module_name="vertexai.preview.reasoning_engines",
        )
        # We use `._get_gca_resource(...)` instead of `created_resource` to
        # fully instantiate the attributes of the reasoning engine.
        sdk_resource._gca_resource = sdk_resource._get_gca_resource(
            resource_name=created_resource.name
        )
        sdk_resource.execution_api_client = initializer.global_config.create_client(
            client_class=aip_utils.ReasoningEngineExecutionClientWithOverride,
            credentials=sdk_resource.credentials,
            location_override=sdk_resource.location,
        )
        try:
            _register_api_methods_or_raise(sdk_resource)
        except Exception as e:
            logging.warning("Failed to register API methods: {%s}", e)
        sdk_resource._operation_schemas = None
        return sdk_resource


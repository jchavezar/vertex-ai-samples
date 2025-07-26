FROM --platform=amd64 ubuntu:20.04
ENV GCSFUSE_REPO gcsfuse-stretch

USER root

# Add google repositories for gcsfuse and google cloud sdk
RUN apt-get update -y && apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl gnupg
RUN echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

# Install gcsfuse and google cloud sdk
RUN apt-get update -y  && apt-get install -y gcsfuse google-cloud-sdk \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
ENTRYPOINT ["gcsfuse"]

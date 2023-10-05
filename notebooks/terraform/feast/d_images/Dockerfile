FROM python:3.9

RUN pip install feast
RUN feast init feature_repo
WORKDIR /feature_repo/feature_repo
RUN feast apply
RUN feast materialize-incremental $(date +%Y-%m-%d)

EXPOSE 6566

CMD ["feast", "serve"]

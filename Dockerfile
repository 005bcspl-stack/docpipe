FROM python:3.12-slim
WORKDIR /app
COPY docpipe ./docpipe
COPY templates ./templates
COPY data ./data
ENTRYPOINT ["python", "-m", "docpipe"]
CMD ["generate"]

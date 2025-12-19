FROM python:3.10-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git libgomp1 build-essential cmake \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python deps — ensure backslashes have no trailing spaces
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir \
        numpy \
        torch \
        torchvision \
        autogluon.timeseries \
        boto3 \
        dvc[s3]

# create necessary dirs (optional but explicit)
RUN mkdir -p ./models ./data

# Copy only needed files (dest is relative to WORKDIR)
COPY deploy/app.py ./app.py
COPY models/autogluonTS.dvc ./models/autogluonTS.dvc
COPY src/tests/dummy_data.csv ./data/dummy.csv
COPY deploy/start.sh ./start.sh

# initialise dvc (creates /app/.dvc because WORKDIR=/app)
RUN dvc init --no-scm

# configure remote (will write into /app/.dvc/config)
RUN dvc remote add -d storage s3://baswap

# show config for build logs
RUN cat .dvc/config

# add runtime entrypoint script and make executable
RUN chmod +x ./start.sh

ENTRYPOINT ["./start.sh"]
CMD ["--input-csv","./data/dummy.csv","--model-name","autogluon_h"]

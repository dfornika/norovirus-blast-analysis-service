# Norovirus BLAST Analysis Service

## Dev Setup

```
git clone git@github.com:dfornika/norovirus-blast-analysis-service.git
cd norovirus-blast-analysis-service
conda create -n norovirus-blast-analysis-service python=3 pip
conda activate norovirus-blast-analysis-service
pip install -e .
```

To create a new database and run migrations, run:

```
./scripts/regen_db.sh
```

To start the server, run:

```
./scripts/start.sh
```

To initiate an analysis, use `curl`, Postman or some other HTTP tool to POST a message to the endpoint `/analysis/submission` in json format like this:

```json
{
  "sequences": [
      {
          "id": "SAMPLE-01",
          "sequence": ""
      },
      {
          "id": "SAMPLE-02",
          "sequence": ""
      }
  ]
}
```

The response will be something like:

```json
{
  "analysis_uuid": "5108222c-3850-491b-bc4a-06761d0f6fc8",
  "status": "QUEUED"
}
```

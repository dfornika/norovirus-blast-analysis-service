import argparse
import csv
import json
import logging
import os
import subprocess

from pathlib import Path
from logging.config import fileConfig

import uvicorn

from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas, config, deps
from .database import SessionLocal, engine

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'), disable_existing_loggers=False)
logger = logging.getLogger(__name__)


app = FastAPI()

origins = [
    "http://localhost:9500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def store_blast_results(analysis: models.Analysis, blast_results_path: Path, db: Session):
    """
    Store a set of blast analysis results to the database.

    :param analysis: The analysis object
    :type analysis: models.Analysis
    :param blast_results_path: The path to the blast results file
    :type blast_results_path: Path
    :return: None
    :rtype: None
    """
    int_fields = [
        'query_length',
        'query_start',
        'query_end',
        'subject_length',
        'subject_start',
        'subject_end',
        'alignment_length',
        'num_mismatch',
        'num_gaps',
        'bitscore',
    ]
    float_fields = [
        'percent_identity',
        'percent_coverage',
        'e_value',
    ]
    analysis_fk = analysis.pk
    analysis_result = models.AnalysisResult(
        analysis_fk=analysis_fk,
    )
    db.add(analysis_result)
    db.commit()
    db.refresh(analysis_result)
    with open(blast_results_path, 'r') as f:
        reader = csv.DictReader(f, dialect='unix')
        for row in reader:
            for field in int_fields:
                try:
                    row[field] = int(row[field])
                except ValueError as e:
                    row[field] = None
            for field in float_fields:
                try:
                    row[field] = float(row[field])
                except ValueError as e:
                    row[field] = None
            db_blast_record = models.BlastRecord(
                analysis_result_fk=analysis_result.pk,
                query_seq_id=row['query_seq_id'],
                subject_accession=row['subject_accession'],
                subject_strand=row['subject_strand'],
                query_length=row['query_length'],
                query_start=row['query_start'],
                query_end=row['query_end'],
                subject_length=row['subject_length'],
                subject_start=row['subject_start'],
                subject_end=row['subject_end'],
                alignment_length=row['alignment_length'],
                percent_identity=row['percent_identity'],
                percent_coverage=row['percent_coverage'],
                num_mismatch=row['num_mismatch'],
                num_gaps=row['num_gaps'],
                e_value=row['e_value'],
                bitscore=row['bitscore'],
                subject_taxids = row['subject_taxids'],
                subject_names = row['subject_names'],
                genus = row['genus'],
                species = row['species'],
                database_name = row['database_name'],
                database_version = row['database_version'],
                database_date = row['database_date'],
            )
            db.add(db_blast_record)

        analysis.status = "COMPLETED"
        db.commit()
        
        
def run_analysis(analysis: models.Analysis, db: Session):
    """
    Run the analysis.

    :param analysis: The analysis object
    :type analysis: models.Analysis
    :param db: The database session
    :type db: Session
    :return: The analysis object
    :rtype: models.Analysis
    """
    analysis_dir = os.path.join('test_analysis', analysis.analysis_uuid)
    os.makedirs(analysis_dir, exist_ok=True)
    with open(os.path.join(analysis_dir, 'input.fa'), 'w') as f:
        for sequence in analysis.input_sequences:
            f.write(f">{sequence.id}\n")
            f.write(f"{sequence.sequence}\n")

    nextflow_cmd = [
        'nextflow',
        'run',
        'BCCDC-PHL/norovirus-blast-nf',
        '-r', 'main',
        '-profile', 'conda',
        '--cache', os.path.join(os.path.expanduser('~'), '.conda/envs'),
        '--fasta_input', os.path.join(analysis_dir),
        '--db', '/home/dfornika/code/norovirus-blast-nf/db.fa',
        '--outdir', os.path.join(analysis_dir, 'norovirus-blast-nf-v0.1-output'),
        '-with-trace', os.path.join(analysis_dir, 'norovirus-blast-nf-v0.1-output', analysis.analysis_uuid + '_nextflow_trace.tsv'),
        '-with-report', os.path.join(analysis_dir, 'norovirus-blast-nf-v0.1-output', analysis.analysis_uuid + '_nextflow_report.html'),
        '-work-dir', os.path.join('/home/dfornika/scratch/work-norovirus-blast-nf', analysis.analysis_uuid),
    ]
    logger.info(f"Running analysis {analysis.analysis_uuid}")
    analysis.status = "RUNNING"
    db.commit()
    result = subprocess.run(nextflow_cmd, check=True, capture_output=True, text=True)
    if result.returncode == 0:
        logger.info(f"Analysis {analysis.analysis_uuid} completed successfully")
        analysis.status = "SUCCESS"
        blast_results_path = os.path.join(analysis_dir, '16s-nf-v0.1-output', 'collected_blast.csv')
        if os.path.exists(blast_results_path):
            logger.info(f"Storing blast results for analysis {analysis.analysis_uuid}")
            store_blast_results(analysis, blast_results_path, db)
            logger.info(f"Stored blast results for analysis {analysis.analysis_uuid}")
    else:
        logger.error(f"Analysis {analysis.analysis_uuid} failed")
        analysis.status = "FAILED"
    return analysis


@app.post("/analysis/submission")
async def accept_analysis_submission(analysis: schemas.AnalysisSubmissionRequest, background_tasks: BackgroundTasks, response_model=schemas.AnalysisSubmissionResponse, db: Session=Depends(deps.get_db)):
    db_analysis = crud.create_analysis_submission(db, analysis)
    background_tasks.add_task(run_analysis, db_analysis, db)
    
    return db_analysis


@app.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str, db: Session=Depends(deps.get_db)):
    db_analysis = crud.get_analysis_by_uuid(db, analysis_id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return db_analysis


@app.get("/analysis/{analysis_id}/results")
async def get_analysis_status(analysis_id: str, db: Session=Depends(deps.get_db)):
    db_analysis_results = crud.get_analysis_results_by_uuid(db, analysis_id)
    if db_analysis_results is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return db_analysis_results



def main(args=None):
    if args is None:

        uvicorn.run(app)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the norovirus_blast_analysis API.')
    parser.add_argument('--config', help='The path to the config file')
    args = parser.parse_args()
    main(args)

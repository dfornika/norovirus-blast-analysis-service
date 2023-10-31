import uuid

from sqlalchemy.orm import Session

from . import models, schemas


def create_analysis_submission(db: Session, analysis: schemas.AnalysisSubmissionRequest):
    """
    """
    analysis_uuid = str(uuid.uuid4())
    db_analysis = models.Analysis(
        analysis_uuid=analysis_uuid,
        status="QUEUED",
    )
    db.add(db_analysis)
    sequences = analysis.sequences
    for sequence in sequences:
        db_sequence = models.InputSequence(
            id=sequence['id'],
            analysis=db_analysis,
            sequence=sequence['sequence'],
        )
        db.add(db_sequence)

    db.commit()
    db.refresh(db_analysis)    

    return db_analysis


def get_analysis_submissions(db: Session):
    """
    """
    analysis_submissions = db.query(models.Analysis).all()
    return analysis_submissions


def get_analysis_by_uuid(db: Session, analysis_uuid: str):
    """
    """
    analysis = db.query(models.Analysis).filter(models.Analysis.analysis_uuid == analysis_uuid).first()
    return analysis


def get_analysis_results_by_uuid(db: Session, analysis_uuid: str):
    """
    """
    analysis = db.query(models.Analysis).filter(models.Analysis.analysis_uuid == analysis_uuid).first()
    analysis_result = db.query(models.AnalysisResult).filter(models.AnalysisResult.analysis == analysis).first()
    blast_records = db.query(models.BlastRecord).filter(models.BlastRecord.analysis_result == analysis_result).all()
    return blast_records

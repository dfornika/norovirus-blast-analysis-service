from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .database import Base


class Analysis(Base):
    __tablename__ = "analysis"

    pk = Column(Integer, primary_key=True, index=True)
    analysis_uuid = Column(String, index=True)
    status = Column(String, index=True)

    input_sequences = relationship("InputSequence", back_populates="analysis")
    analysis_results = relationship("AnalysisResult", back_populates="analysis")


class AnalysisResult(Base):
    __tablename__ = "analysis_result"

    pk = Column(Integer, primary_key=True, index=True)
    analysis_fk = Column(Integer, ForeignKey("analysis.pk"))

    analysis = relationship("Analysis", back_populates="analysis_results")
    blast_records = relationship("BlastRecord", back_populates="analysis_result")


class InputSequence(Base):
    __tablename__ = "input_sequence"

    pk = Column(Integer, primary_key=True, index=True)
    id = Column(String, index=True)
    analysis_fk = Column(Integer, ForeignKey("analysis.pk"))
    sequence = Column(String)
    sequence_length = Column(Integer)
    num_ambiguous_bases = Column(Integer)
    num_n_bases = Column(Integer)

    analysis = relationship("Analysis", back_populates="input_sequences")


class BlastDatabase(Base):
    __tablename__ = "blast_database"

    pk = Column(Integer, primary_key=True, index=True)
    database_id = Column(String)
    database_name = Column(String)
    database_version = Column(String)
    database_date = Column(String)
    database_path = Column(String)


class BlastRecord(Base):
    __tablename__ = "blast_record"

    pk = Column(Integer, primary_key=True, index=True)
    analysis_result_fk = Column(Integer, ForeignKey("analysis_result.pk"))
    blast_database_fk = Column(Integer, ForeignKey("blast_database.pk"))
    query_seq_id = Column(String)
    subject_accession = Column(String)
    subject_strand = Column(String)
    query_length = Column(Integer)
    query_start = Column(Integer)
    query_end = Column(Integer)
    subject_length = Column(Integer)
    subject_start = Column(Integer)
    subject_end = Column(Integer)
    alignment_length = Column(Integer)
    percent_identity = Column(Float)
    percent_coverage = Column(Float)
    num_mismatch = Column(Integer)
    num_gaps = Column(Integer)
    e_value = Column(Float)
    bitscore = Column(Integer)
    accession = Column(String)
    genotype = Column(String)
    region = Column(String)
    database_name = Column(String)
    database_version = Column(String)
    database_date = Column(String)

    analysis_result = relationship("AnalysisResult", back_populates="blast_records")
    blast_database = relationship("BlastDatabase")

#!/usr/bin/env bash

export NOROVIRUS_BLAST_DATABASE_URI="sqlite:///app.db"

uvicorn norovirus_blast_analysis.main:app --reload

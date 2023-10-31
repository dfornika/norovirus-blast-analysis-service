#!/bin/bash

db_name="app"
export NOROVIRUS_BLAST_DATABASE_URI="sqlite:///${db_name}.db"

rm ${db_name}.db
rm alembic/versions/*.py
alembic revision --autogenerate -m 'init'
alembic upgrade head

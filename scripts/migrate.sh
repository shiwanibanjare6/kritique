#!/bin/bash
set -e
cd backend
python - <<'PY'
from app.database.db import Base, engine
from app.database.models import Review
Base.metadata.create_all(bind=engine)
print('Database initialized')
PY

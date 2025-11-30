Set-Location C:\project_bmad\pet-adoption-platform\backend
$env:PYTHONPATH = $PWD.Path
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --port 8000" -RedirectStandardError "stderr.log" -RedirectStandardOutput "stdout.log" -NoNewWindow -PassThru
Start-Sleep -Seconds 5
curl.exe -i -X POST http://localhost:8000/claims -H "Content-Type: application/json" -d "{}"
Stop-Process -Name "python" -Force

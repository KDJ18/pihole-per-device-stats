# Pi-hole Per-Device Stats

Python dashboard that shows the top blocked domains for each device on my home network, using the Pi-hole v6 API.

> 🚧 Work in progress

## Current status
- [x] Pi-hole running on a Raspberry Pi (Ubuntu)
- [x] Script that logs into the Pi-hole API and groups blocked domains by device
- [x] Pull the last 24 hours of queries with paging
- [ ] FastAPI service with `/devices` endpoints
- [ ] Web dashboard
- [ ] Docker deployment on the Pi

## Setup
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then add your Pi-hole URL and password
python explore.py
```

"""Create local settings once; never overwrite an existing database or .env."""
from pathlib import Path
import secrets
root=Path(__file__).resolve().parents[1]
f=root/'backend'/'.env'
if not f.exists():
    text=(root/'backend'/'.env.example').read_text().replace('replace-with-a-long-random-value',secrets.token_urlsafe(48))
    f.write_text(text,encoding='utf-8')
    print('Created local .env. No database deleted.')
else: print('Using existing .env and database.')

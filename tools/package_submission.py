"""Produce a clean source hand-in without runtime data or credentials."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[1]
out=root.parent/'RankAfrica-Lecturer-Submission.zip'
excluded={'.git','.venv','node_modules','__pycache__','.pytest_cache','uploads','dist','frontend_dist'}
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if not p.is_file() or any(x in excluded for x in rel.parts):continue
        if p.name=='.env' or (p.name.startswith('.env.') and not p.name.endswith('.example')):continue
        if p.suffix in {'.db','.sqlite','.sqlite3','.pyc','.log'}:continue
        z.write(p,Path(root.name)/rel)
print(out)

Set-Location "$PSScriptRoot/frontend"
if (!(Test-Path .env)) { Copy-Item .env.example .env }
npm ci
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm run dev

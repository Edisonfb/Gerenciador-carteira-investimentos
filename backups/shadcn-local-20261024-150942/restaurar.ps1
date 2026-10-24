$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$files = @(
  'frontend/src/styles/shadcn.css',
  'frontend/src/main.tsx',
  'frontend/src/pages/CarteirasInvestidorPage.tsx'
)
foreach ($file in $files) {
  $source = Join-Path $PSScriptRoot $file
  if (-not (Test-Path -LiteralPath $source)) { throw "Backup ausente: $file" }
}
foreach ($file in $files) {
  Copy-Item -LiteralPath (Join-Path $PSScriptRoot $file) -Destination (Join-Path $projectRoot $file) -Force
}
Write-Host 'Configuracao anterior do tema restaurada.'

Write-Host "Generating stubs for pyodas2..."

$env:PYTHONPATH = "$env:PYTHONPATH;$PWD"
pybind11-stubgen pyodas2 -o $PWD

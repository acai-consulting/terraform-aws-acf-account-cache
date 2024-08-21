$scriptpath = $MyInvocation.MyCommand.Path
$dir = Split-Path $scriptpath
Set-Location -Path $dir

python3 -m unittest json_pattern_engine_test
python3 -m unittest context_cache_query_test
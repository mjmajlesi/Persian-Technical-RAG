param(
    [string[]]$Packs = @('c', 'cpp', 'python', 'java'),
    [switch]$Force,
    [switch]$Run
)

[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false
$OutputEncoding = [Console]::OutputEncoding
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$expected = @{ c = 503; cpp = 201; python = 253; java = 73 }
$selected = @($Packs | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim().ToLowerInvariant() } | Select-Object -Unique)

function Invoke-Step([string]$Stage, [string]$Program, [string[]]$Arguments) {
    Write-Host "[$Stage] در حال اجرا / Running"
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "[$Stage] فرمان شکست خورد / Command failed (exit $LASTEXITCODE)" }
}

try {
    if (-not $selected.Count -or @($selected | Where-Object { -not $expected.ContainsKey($_) }).Count) {
        throw '[Packs] پک نامعتبر؛ از c,cpp,python,java استفاده کنید / Invalid pack; use c,cpp,python,java'
    }
    Set-Location -LiteralPath $root
    Write-Host '[Python] بررسی Python 3.11 / Checking Python 3.11'
    $python = $null
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $ErrorActionPreference = 'Continue'
        $candidate = & $launcher.Source -3.11 -c 'import sys; print(sys.executable)' 2>$null
        $code = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($code -eq 0) { $python = $candidate | Select-Object -Last 1 }
        if (-not $python) {
            $ErrorActionPreference = 'Continue'
            $registered = & $launcher.Source -0p 2>$null
            $ErrorActionPreference = 'Stop'
            foreach ($line in $registered) {
                if ($line -match '([A-Za-z]:\\.*?python(?:\.exe))\s*$') {
                    $candidate = $Matches[1].Trim()
                    & $candidate -c 'import sys; sys.exit(sys.version_info[:2] != (3, 11))'
                    if ($LASTEXITCODE -eq 0) { $python = $candidate; break }
                }
            }
        }
    }
    if (-not $python) {
        $candidate = Get-Command python3.11 -ErrorAction SilentlyContinue
        if ($candidate) { $python = $candidate.Source }
    }
    if (-not $python) { throw '[Python] Python 3.11 نصب نیست؛ آن را از python.org نصب کنید / Python 3.11 missing; install it from python.org' }
    & $python -c 'import sys; sys.exit(sys.version_info[:2] != (3, 11))'
    if ($LASTEXITCODE -ne 0) { throw '[Python] Python 3.11 لازم است؛ آن را از python.org نصب کنید / Python 3.11 required; install it from python.org' }

    $venv = Join-Path $root '.venv'
    $venvPython = Join-Path $venv 'Scripts\python.exe'
    if (Test-Path -LiteralPath $venv) {
        if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
            throw '[venv] محیط موجود نامعتبر است؛ آن را دستی جابه‌جا یا حذف کنید و دوباره اجرا کنید / Existing .venv is invalid; move or remove it manually, then rerun'
        }
        & $venvPython -c 'import os,sys; sys.exit(not (sys.version_info[:2] == (3,11) and os.path.samefile(sys._base_executable, sys.argv[1])))' $python
        if ($LASTEXITCODE -ne 0) {
            throw '[venv] محیط موجود با مفسر دیگری ساخته شده؛ آن را دستی جابه‌جا یا حذف کنید و دوباره اجرا کنید / Existing .venv uses another interpreter; move or remove it manually, then rerun'
        }
        Write-Host '[venv] محیط موجود سازگار است / Existing environment is compatible'
    } else {
        Invoke-Step 'venv' $python @('-m', 'venv', $venv)
    }
    Invoke-Step 'pip' $venvPython @('-m', 'pip', 'install', '--index-url', 'https://pypi.org/simple', '-r', 'requirements-lock.txt')
    Invoke-Step 'pip check' $venvPython @('-m', 'pip', 'check')
    if (-not (Test-Path -LiteralPath '.env')) {
        $content = [System.IO.File]::ReadAllBytes((Join-Path $root '.env.example'))
        $file = [System.IO.File]::Open((Join-Path $root '.env'), [System.IO.FileMode]::CreateNew)
        try { $file.Write($content, 0, $content.Length) } finally { $file.Dispose() }
        Write-Host '[env] ساخته شد؛ فقط LLM_API_KEY، LLM_BASE_URL و LLM_MODEL را تنظیم کنید؛ تا آن زمان فقط مسیر بدون تولید پاسخ کار می‌کند / Created; set only LLM_API_KEY, LLM_BASE_URL and LLM_MODEL; until then only paths without answer generation work'
    } else {
        Write-Host '[env] فایل موجود حفظ شد / Existing file preserved'
    }

    $warned = $false
    foreach ($lang in $selected) {
        $dir = Join-Path 'data/index' $lang
        $chunks = Join-Path $dir 'chunks.jsonl'
        $ready = (Test-Path -LiteralPath (Join-Path $dir 'faiss.index') -PathType Leaf) -and
                 (Test-Path -LiteralPath $chunks -PathType Leaf) -and
                 (Test-Path -LiteralPath (Join-Path $dir 'ids.json') -PathType Leaf)
        if ($ready) {
            $count = [System.IO.File]::ReadAllLines((Join-Path $root $chunks)).Length
            $ready = $count -eq $expected[$lang]
        }
        if ($ready -and -not $Force) {
            Write-Host "[$lang] ایندکس آماده است؛ ساخت رد شد / Index ready; build skipped ($count chunks)"
            continue
        }
        Invoke-Step "ingest $lang" $venvPython @('-m', 'src.ingest', '--lang', $lang)
        $count = [System.IO.File]::ReadAllLines((Join-Path $root $chunks)).Length
        if ($count -ne $expected[$lang]) { throw "[$lang] تعداد Chunk نادرست است / Unexpected chunk count: $count" }
        if (-not $warned) {
            Write-Host '[Index] دانلود اولیه مدل embedding ممکن است طول بکشد / First embedding-model download may take a while'
            $warned = $true
        }
        Invoke-Step "index $lang" $venvPython @('-m', 'src.index', 'build', '--lang', $lang)
        foreach ($name in @('faiss.index', 'chunks.jsonl', 'ids.json')) {
            if (-not (Test-Path -LiteralPath (Join-Path $dir $name) -PathType Leaf)) {
                throw "[$lang] فایل ایندکس وجود ندارد / Index file missing: $name"
            }
        }
    }
    foreach ($lang in $selected) { Write-Host "[$lang] آماده / Ready: $($expected[$lang]) chunks" }
    Write-Host '[Server] اجرا / Run: .\.venv\Scripts\python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000'
    Write-Host '[Server] نشانی / URL: http://127.0.0.1:8000'
    if ($Run) { Invoke-Step 'server' $venvPython @('-m', 'uvicorn', 'src.web.app:app', '--host', '127.0.0.1', '--port', '8000') }
} catch {
    [Console]::Error.WriteLine("[Error] خطای راه‌اندازی / Setup failed: $($_.Exception.Message)")
    exit 1
}

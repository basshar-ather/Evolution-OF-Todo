param(
    [string]$ImageTag = "evo-todo-backend:local",
    [string]$Registry = "",
    [switch]$Push
)

# Use script-relative paths to ensure correct Docker build context regardless of CWD
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..")
$backendBuildContext = Join-Path $repoRoot "phases\phase-1\backend"
$dockerfile = Join-Path $repoRoot "phases\phase-4\backend\Dockerfile"

Write-Output "Building Docker image: $ImageTag"
docker build -t $ImageTag -f "$dockerfile" "$backendBuildContext"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed. Ensure Docker Desktop is running and the daemon is available."
    exit 1
}

# Run container (exposes 8000)
$name = "evo-todo-test"
Write-Output "Running container $name from $ImageTag"
docker run -d --rm -p 8000:8000 --name $name -e DATABASE_URL="sqlite:////data/database.db" -v "${PWD}\tmp_data:/data" $ImageTag
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start container"
    exit 1
}

# Wait for health check
$url = "http://127.0.0.1:8000/health"
$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline) {
    try {
        $r = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 2
        if ($r.status -eq 'ok') {
            Write-Output "Health check OK"
            break
        }
    } catch {
        Start-Sleep -Milliseconds 500
    }
}

if ((Get-Date) -ge $deadline) {
    Write-Error "Health check failed within 30s"
    docker logs $name --tail 100
    docker stop $name | Out-Null
    exit 1
}

Write-Output "Stopping container"
docker stop $name | Out-Null

if ($Push -and $Registry) {
    $fullTag = "$Registry/$ImageTag"
    Write-Output "Tagging $ImageTag as $fullTag and pushing"
    docker tag $ImageTag $fullTag
    docker push $fullTag
}

Write-Output "Done."

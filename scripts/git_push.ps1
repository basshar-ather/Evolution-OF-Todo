param(
    [string]$RemoteUrl = $env:GIT_REMOTE,
    [string]$Branch = "phase/completed",
    [string]$Tag = "v0.1.0",
    [switch]$Force
)

if (-not $RemoteUrl) {
    Write-Error "Remote URL is required. Provide --RemoteUrl or set GIT_REMOTE environment variable."
    exit 1
}

Write-Output "Using remote: $RemoteUrl"

# If a token is provided in GIT_TOKEN and the URL is HTTPS, build a push URL that includes the token.
$pushUrl = $RemoteUrl
if ($env:GIT_TOKEN -and $RemoteUrl -like 'https://*') {
    try {
        $u = [uri]$RemoteUrl
        $pushUrl = "https://$($env:GIT_TOKEN)@$($u.Host)$($u.AbsolutePath)"
        Write-Output "Using token-authenticated push URL (will not persist token in git remote)."
    } catch {
        Write-Warning "Failed to construct tokenized push URL; falling back to provided remote URL."
        $pushUrl = $RemoteUrl
    }
}

# Ensure remote exists (set to provided remote URL)
git remote remove origin 2>$null
git remote add origin $RemoteUrl

Write-Output "Pushing branch '$Branch' to remote..."
git push $pushUrl $Branch
if ($LASTEXITCODE -ne 0) {
    if ($Force) {
        Write-Output "Initial push failed; retrying with force..."
        git push $pushUrl $Branch -f
    } else {
        Write-Error "Push failed. Rerun with -Force to force push, or provide credentials."
        exit 1
    }
}

Write-Output "Pushing tag '$Tag' to remote..."
git push $pushUrl refs/tags/$Tag
if ($LASTEXITCODE -ne 0) {
    if ($Force) {
        git push $pushUrl refs/tags/$Tag -f
    } else {
        Write-Error "Tag push failed. Rerun with -Force to force push, or provide credentials."
        exit 1
    }
}

Write-Output "Push complete. Remote: $RemoteUrl, Branch: $Branch, Tag: $Tag"

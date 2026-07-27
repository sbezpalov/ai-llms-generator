<#
.SYNOPSIS
    Install the AIO skill suite into a project's .cursor/skills folder.

.PARAMETER Target
    Destination project root (default: current directory). Must not contain '..'.
#>
[CmdletBinding()]
param (
    [string]$Target = "."
)

$ErrorActionPreference = "Stop"

if ($Target -match '\.\.') {
    throw "Refusing Target containing '..': $Target"
}

$Root = Split-Path -Parent $PSScriptRoot
$SkillsRoot = Join-Path $Target ".cursor/skills"
New-Item -ItemType Directory -Force -Path $SkillsRoot | Out-Null

function Install-SkillDir {
    param ([string]$Name, [string]$Source)
    $Dest = Join-Path $SkillsRoot $Name
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
    Copy-Item -Force -Recurse -Path (Join-Path $Source "*") -Destination $Dest
    Write-Host "Installed $Name → $Dest"
}

$Gen = Join-Path $SkillsRoot "generate-llms-txt"
New-Item -ItemType Directory -Force -Path $Gen | Out-Null
Copy-Item -Force `
    (Join-Path $Root "SKILL.md"), `
    (Join-Path $Root "PROMPT.md"), `
    (Join-Path $Root "template-llms.txt"), `
    (Join-Path $Root "example-llms.txt") `
    -Destination $Gen
Write-Host "Installed generate-llms-txt → $Gen"

Install-SkillDir "audit-robots-ai-bots" (Join-Path $Root "skills/audit-robots-ai-bots")
Install-SkillDir "draft-json-ld" (Join-Path $Root "skills/draft-json-ld")
Install-SkillDir "aio-site-audit" (Join-Path $Root "skills/aio-site-audit")

Write-Host "AIO suite ready under $SkillsRoot"

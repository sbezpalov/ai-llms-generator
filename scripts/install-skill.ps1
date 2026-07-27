<#
.SYNOPSIS
    Copy generate-llms-txt skill into a project's .cursor/skills folder.

.PARAMETER Target
    Destination project root (default: current directory).
#>
[CmdletBinding()]
param (
    [string]$Target = "."
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Dest = Join-Path $Target ".cursor/skills/generate-llms-txt"

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Copy-Item -Force `
    (Join-Path $Root "SKILL.md"), `
    (Join-Path $Root "PROMPT.md"), `
    (Join-Path $Root "template-llms.txt"), `
    (Join-Path $Root "example-llms.txt") `
    -Destination $Dest

Write-Host "Installed generate-llms-txt → $Dest"

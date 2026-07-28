<#
.SYNOPSIS
    Install the AIO skill suite into a project's .cursor/skills folder.

.PARAMETER Target
    Existing destination project root (default: current directory).

.PARAMETER Force
    Back up existing skill directories, then install clean copies.

.PARAMETER DryRun
    Show planned actions without writing files.
#>
[CmdletBinding()]
param (
    [Parameter(Position = 0)]
    [string]$Target = ".",

    [switch]$Force,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ResolvedTarget = Resolve-Path -LiteralPath $Target
if (-not (Test-Path -LiteralPath $ResolvedTarget.Path -PathType Container)) {
    throw "Target must be an existing directory: $Target"
}

$Root = Split-Path -Parent $PSScriptRoot
$SkillsRoot = Join-Path $ResolvedTarget.Path ".cursor/skills"
$BackupSuffix = ".backup-$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))"

$Skills = @(
    [pscustomobject]@{
        Name = "generate-llms-txt"
        Source = $Root
        Files = @(
            "SKILL.md",
            "PROMPT.md",
            "PROMPT.ru.md",
            "template-llms.txt",
            "example-llms.txt"
        )
    },
    [pscustomobject]@{
        Name = "audit-robots-ai-bots"
        Source = Join-Path $Root "skills/audit-robots-ai-bots"
        Files = $null
    },
    [pscustomobject]@{
        Name = "draft-json-ld"
        Source = Join-Path $Root "skills/draft-json-ld"
        Files = $null
    },
    [pscustomobject]@{
        Name = "aio-site-audit"
        Source = Join-Path $Root "skills/aio-site-audit"
        Files = $null
    }
)

$Destinations = foreach ($Skill in $Skills) {
    [pscustomobject]@{
        Skill = $Skill
        Path = Join-Path $SkillsRoot $Skill.Name
    }
}

# Preflight every destination before making any change.
foreach ($Destination in $Destinations) {
    if (Test-Path -LiteralPath $Destination.Path) {
        if (-not $Force) {
            throw ("Refusing to overwrite existing skill: {0}. " +
                "Re-run with -Force to create a backup and install a clean copy." -f
                $Destination.Path)
        }
        $BackupPath = "$($Destination.Path)$BackupSuffix"
        if (Test-Path -LiteralPath $BackupPath) {
            throw "Backup destination already exists: $BackupPath"
        }
    }
}

if ($DryRun) {
    foreach ($Destination in $Destinations) {
        if (Test-Path -LiteralPath $Destination.Path) {
            Write-Host "Would back up $($Destination.Path) → $($Destination.Path)$BackupSuffix"
        }
        Write-Host "Would install $($Destination.Skill.Name) → $($Destination.Path)"
    }
    return
}

New-Item -ItemType Directory -Force -Path $SkillsRoot | Out-Null

foreach ($Destination in $Destinations) {
    $Skill = $Destination.Skill
    $Dest = $Destination.Path

    if (Test-Path -LiteralPath $Dest) {
        $BackupPath = "$Dest$BackupSuffix"
        Move-Item -LiteralPath $Dest -Destination $BackupPath
        Write-Host "Backed up $Dest → $BackupPath"
    }

    New-Item -ItemType Directory -Path $Dest | Out-Null

    if ($null -ne $Skill.Files) {
        foreach ($File in $Skill.Files) {
            Copy-Item -LiteralPath (Join-Path $Skill.Source $File) -Destination $Dest
        }
    }
    else {
        Get-ChildItem -LiteralPath $Skill.Source -Force |
            Copy-Item -Destination $Dest -Recurse -Force
    }

    Write-Host "Installed $($Skill.Name) → $Dest"
}

Write-Host "AIO suite ready under $SkillsRoot"

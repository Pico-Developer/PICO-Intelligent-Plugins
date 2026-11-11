[CmdletBinding()]
param(
    [string]$ProjectPath,
    [string]$TargetRepo,
    [string]$UnityEditorPath,
    [string]$ReportPath,
    [ValidateSet('warn', 'fail')]
    [string]$PageSizePolicy = 'warn',
    [switch]$PreflightOnly,
    [switch]$ValidateOnly,
    [switch]$KeepWorkDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pythonCommands = if ($IsMacOS) { @('python3', 'python') } else { @('python', 'python3') }
$python = $null
foreach ($commandName in $pythonCommands) {
    $command = Get-Command $commandName -ErrorAction SilentlyContinue
    if (-not $command) {
        continue
    }
    $versionText = & $command.Source -c `
        'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>$null
    if ($LASTEXITCODE -eq 0 -and [version]$versionText -ge [version]'3.9') {
        $python = $command.Source
        break
    }
}
if (-not $python) {
    throw 'Python 3.9 or newer is required.'
}

$core = Join-Path $PSScriptRoot 'Export-VibeLabAndroid.py'
$arguments = @($core)
if ($ProjectPath) { $arguments += @('--project-path', $ProjectPath) }
if ($TargetRepo) { $arguments += @('--target-repo', $TargetRepo) }
if ($UnityEditorPath) { $arguments += @('--unity-editor-path', $UnityEditorPath) }
if ($ReportPath) { $arguments += @('--report-path', $ReportPath) }
$arguments += @('--page-size-policy', $PageSizePolicy)
if ($PreflightOnly) { $arguments += '--preflight-only' }
if ($ValidateOnly) { $arguments += '--validate-only' }
if ($KeepWorkDir) { $arguments += '--keep-work-dir' }

& $python @arguments
exit $LASTEXITCODE

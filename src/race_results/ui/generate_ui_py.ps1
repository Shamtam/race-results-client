# assumes PowerShell 7 (to ensure UTF-8 without BOM for exported py files)
Get-ChildItem *.ui | ForEach-Object{
    pyside6-uic.exe $_ > "$($_.BaseName).py"
}
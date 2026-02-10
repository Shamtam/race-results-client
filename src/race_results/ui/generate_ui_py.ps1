# assumes PowerShell 7 (to ensure UTF-8 without BOM for exported py files)
Get-ChildItem *.ui | ForEach-Object{
    rm "$($_.BaseName).py"
    pyside6-uic.exe --from-imports $_ > "$($_.BaseName).py"
}

Get-ChildItem *.qrc | ForEach-Object{
    rm "$($_.BaseName)_rc.py"
    pyside6-rcc.exe $_ > "$($_.BaseName)_rc.py"
}
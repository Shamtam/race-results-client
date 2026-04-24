Param([string]$infile)
magick.exe convert -density 384 -background transparent $infile -define icon:auto-resize=256,128,64,48,32,24,16 "$($(Get-Item $infile).Basename).ico"
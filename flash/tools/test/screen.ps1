param([string]$Out, [int]$Width = 960)
# Capture the whole primary screen (what the player actually sees), scaled down to $Width pixels wide.
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$full = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($full)
$g.CopyFromScreen($b.X, $b.Y, 0, 0, $full.Size)
$h = [int]($b.Height * $Width / $b.Width)
$small = New-Object System.Drawing.Bitmap $full, $Width, $h
$small.Save($Out)
"saved $Out (screen $($b.Width)x$($b.Height))"

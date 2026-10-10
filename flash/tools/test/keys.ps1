param([int]$ProcId, [string[]]$Keys, [int]$HoldMs = 80, [int]$GapMs = 250)
# Focus the window of $ProcId and press each key (virtual-key names like SPACE, RETURN, F9, W, A, S, D, LEFT; "wait:500" pauses; "hold:W:800" holds).
Add-Type @"
using System; using System.Runtime.InteropServices;
public class KI {
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
 [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
 [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint code, uint type);
}
"@
$vk = @{ SPACE=0x20; RETURN=0x0D; ESCAPE=0x1B; LEFT=0x25; UP=0x26; RIGHT=0x27; DOWN=0x28; F=0x46; F2=0x71; F6=0x75; F7=0x76; F8=0x77; F9=0x78; W=0x57; A=0x41; S=0x53; D=0x44; E=0x45; Q=0x51; P=0x50 }
$h = (Get-Process -Id $ProcId).MainWindowHandle
[KI]::ShowWindow($h, 9) | Out-Null
[KI]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 200
function Press([int]$code, [int]$ms) {
  $sc = [byte][KI]::MapVirtualKey($code, 0)
  [KI]::keybd_event([byte]$code, $sc, 0, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds $ms
  [KI]::keybd_event([byte]$code, $sc, 2, [UIntPtr]::Zero)
}
foreach ($k in $Keys) {
  if ($k -like "wait:*") { Start-Sleep -Milliseconds ([int]$k.Split(":")[1]); continue }
  if ($k -like "hold:*") { $p = $k.Split(":"); Press $vk[$p[1]] ([int]$p[2]); Start-Sleep -Milliseconds $GapMs; continue }
  Press $vk[$k] $HoldMs
  Start-Sleep -Milliseconds $GapMs
}
"sent $($Keys -join ' ')"

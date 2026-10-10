// EID Flash launcher ("EID Flash.exe"): starts the modded game in Adobe's Flash Player projector.
//
// Written next to isaac_eid.swf and flashplayer_32_sa.exe by the patcher. It ignores its own command-line
// arguments, so it can be used as a Steam launch option ("...\EID Flash.exe" %command%): Steam appends the
// original game's path, which the projector would otherwise try to open as the movie. It waits for the
// projector to close, so Steam shows the game as running and counts the playtime.
//
// Build (done by flash/tools/make_payload.py with the .NET Framework compiler that ships with Windows):
//   csc /target:winexe /optimize /out:"EID Flash.exe" EIDFlashLauncher.cs
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

[assembly: AssemblyTitle("EID Flash")]
[assembly: AssemblyDescription("Starts The Binding of Isaac (Flash) with External Item Descriptions")]
[assembly: AssemblyProduct("EID Flash (unofficial port of External Item Descriptions)")]

static class EIDFlashLauncher
{
    [STAThread]
    static int Main()
    {
        string dir = AppDomain.CurrentDomain.BaseDirectory;
        string projector = Path.Combine(dir, "flashplayer_32_sa.exe");
        string swf = Path.Combine(dir, "isaac_eid.swf");
        if (!File.Exists(projector) || !File.Exists(swf))
        {
            MessageBox.Show("flashplayer_32_sa.exe and isaac_eid.swf must be in the same folder as EID Flash.exe:\n" + dir +
                            "\n\nRun EID_Flash_Patcher.exe again to recreate them.", "EID Flash",
                            MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
        ProcessStartInfo start = new ProcessStartInfo(projector, "\"" + swf + "\"");
        start.WorkingDirectory = dir;
        start.UseShellExecute = false;
        using (Process game = Process.Start(start))
        {
            game.WaitForExit();
            return game.ExitCode;
        }
    }
}

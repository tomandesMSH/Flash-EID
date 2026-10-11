// EID Flash launcher ("EID Flash.exe"): starts the modded game in Adobe's Flash Player projector.
//
// Written next to isaac_eid.swf and flashplayer_32_sa.exe by the patcher. It can be used as a Steam launch option
// ("...\EID Flash.exe" %command%): Steam appends the original game's path, which is only used to find the game folder
// (the projector would otherwise try to open it as the movie). It waits for the projector to close, so Steam shows
// the game as running and counts the playtime.
//
// Steam achievements: the Steam version sends them with the game's FlashAchievements.exe (through MDM Zinc), which
// the projector can't run. The launcher does it instead: it reads the unlocks from the game's save (the Flash
// SharedObject so.sol, so.data.lock) and runs FlashAchievements.exe from the game folder with the achievement names,
// when it starts (like the Steam version does on every start), whenever the save changes while the game runs, and
// after the game closes. Only achievements unlocked in the save are sent; achievements.log next to the launcher says
// what was sent.
//
// Build (with the .NET Framework compiler that ships with Windows):
//   csc /target:winexe /optimize /out:"EID Flash.exe" EIDFlashLauncher.cs
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;

[assembly: AssemblyTitle("EID Flash")]
[assembly: AssemblyDescription("Starts The Binding of Isaac (Flash) with External Item Descriptions")]
[assembly: AssemblyProduct("EID Flash (unofficial port of External Item Descriptions)")]

static class EIDFlashLauncher
{
    const string Title = "EID Flash";
    const string Movie = "isaac_eid.swf";

    [STAThread]
    static int Main(string[] args)
    {
        string dir = AppDomain.CurrentDomain.BaseDirectory;
        string projector = Path.Combine(dir, "flashplayer_32_sa.exe");
        string swf = Path.Combine(dir, Movie);
        if (!File.Exists(projector) || !File.Exists(swf))
        {
            MessageBox.Show("flashplayer_32_sa.exe and " + Movie + " must be in the same folder as " + Title + ".exe:\n" + dir +
                            "\n\nRun EID_Flash_Patcher.exe again to recreate them.", Title,
                            MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
        Achievements ach = Achievements.Create(args, dir);
        if (ach != null)
        {
            ach.Send(false);
        }
        ProcessStartInfo start = new ProcessStartInfo(projector, "\"" + swf + "\"");
        start.WorkingDirectory = dir;
        start.UseShellExecute = false;
        using (Process game = Process.Start(start))
        {
            while (!game.WaitForExit(3000))
            {
                if (ach != null)
                {
                    ach.Send(false);
                }
            }
            if (ach != null)
            {
                ach.Send(true);
            }
            return game.ExitCode;
        }
    }
}

// Sends the save's unlocked achievements to Steam with the game's own FlashAchievements.exe.
class Achievements
{
    // the game's achievement names by save unlock index (acnam in the game's root script; 0 = not an achievement)
    static readonly string[] Names = {
        null, "Maggy", "Cain", "Judas", "Killed_Mom", null, null, null, "The_Noose", "The_Nail", "The_Quarter", "The_Fetus",
        null, "The_Spider", "The_Spelunker", null, null, null, "The_Rock", "Monstros_Tooth", "Lil_Chubby", "Lokis_Horns",
        null, null, null, "The_Bandage", "The_Cross", "The_Bag", "The_Robo-Baby", "Book_of_Sin", "Gish", "Steven", "Chad",
        "The_Gamekid", "The_Halo", "Mr_Mega", "Pill_Bottle", "Common_Cold", "The_D6", "The_Shears", "The_Parasite", "Baby",
        "Terrible", "The_Wafer", "Money_Power", "It_Lives", "The_Bean", "Moms_Contact", "The_Necronomicon", "Basement_Boy",
        "Cave_Boy", "Depths_Boy", "Womb_Boy", "Golden_God", "Eve", "Moms_Knife", null, null, "The_Razor_Blade",
        "The_Guardian_Angel", "bombs", "The_Demon_Baby", "Forget_Me_Now", "The_Monster_Manual", "a_gift_from_krampus",
        "_d20", "_cross", "_abel", "_horn", "_knife2", "_rainbow", "_bloodlust", "_bloodpenny", "_bloodrights", "_polaroid",
        "_dadskey", "_toe", "_candle", "_burntpenny", "_tail", "_megafetus", "_fish", "_superfan", "_spiderbutt",
        "_counterfeit", "_hairball", "_eggsack", null, "_samson", null, "_platinum" };

    readonly string gameDir;
    readonly HashSet<string> sent = new HashSet<string>();
    DateTime lastWrite;

    Achievements(string gameDir)
    {
        this.gameDir = gameDir;
    }

    // The game folder: from Steam's %command% (the original game's exe), else from game.txt written by the patcher.
    public static Achievements Create(string[] args, string dir)
    {
        foreach (string arg in args)
        {
            try
            {
                string d = Path.GetDirectoryName(arg);
                if (!string.IsNullOrEmpty(d) && File.Exists(Path.Combine(d, "FlashAchievements.exe")))
                {
                    return new Achievements(d);
                }
            }
            catch (ArgumentException)
            {
            }
        }
        try
        {
            string d = File.ReadAllText(Path.Combine(dir, "game.txt")).Trim();
            if (File.Exists(Path.Combine(d, "FlashAchievements.exe")))
            {
                return new Achievements(d);
            }
        }
        catch (Exception)
        {
        }
        return null;
    }

    // The save: so.sol under the Flash Player's SharedObjects ("/" path, so directly in localhost); the newest one
    // if there are several.
    static string SavePath()
    {
        string root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                                   Path.Combine("Macromedia", Path.Combine("Flash Player", "#SharedObjects")));
        string best = null;
        DateTime bestTime = DateTime.MinValue;
        if (!Directory.Exists(root))
        {
            return null;
        }
        foreach (string d in Directory.GetDirectories(root))
        {
            string p = Path.Combine(Path.Combine(d, "localhost"), "so.sol");
            if (File.Exists(p) && File.GetLastWriteTimeUtc(p) > bestTime)
            {
                best = p;
                bestTime = File.GetLastWriteTimeUtc(p);
            }
        }
        return best;
    }

    // Sends the unlocked achievements not sent yet (all of them the first time) when the save has changed.
    public void Send(bool wait)
    {
        try
        {
            string path = SavePath();
            if (path == null || File.GetLastWriteTimeUtc(path) == lastWrite)
            {
                return;
            }
            lastWrite = File.GetLastWriteTimeUtc(path);
            List<string> names = new List<string>();
            foreach (int i in Sol.Unlocked(File.ReadAllBytes(path)))
            {
                if (i < Names.Length && Names[i] != null && !sent.Contains(Names[i]))
                {
                    names.Add(Names[i]);
                }
            }
            if (names.Count == 0)
            {
                return;
            }
            ProcessStartInfo start = new ProcessStartInfo(Path.Combine(gameDir, "FlashAchievements.exe"), string.Join(" ", names.ToArray()));
            start.WorkingDirectory = gameDir;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            using (Process p = Process.Start(start))
            {
                if (!p.WaitForExit(wait ? 30000 : 20000))
                {
                    Log("FlashAchievements.exe didn't finish: " + string.Join(" ", names.ToArray()));
                    return;
                }
                Log("sent (exit code " + p.ExitCode + "): " + string.Join(" ", names.ToArray()));
                if (p.ExitCode == 0)
                {
                    foreach (string n in names)
                    {
                        sent.Add(n);
                    }
                }
            }
        }
        catch (Exception e)
        {
            // no save yet, save being written, Steam not running: tried again on the next change
            lastWrite = DateTime.MinValue;
            Log("not sent: " + e.Message);
        }
    }

    // achievements.log next to the launcher (kept short)
    static void Log(string line)
    {
        try
        {
            string path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "achievements.log");
            if (File.Exists(path) && new FileInfo(path).Length > 100000)
            {
                File.Delete(path);
            }
            File.AppendAllText(path, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "  " + line + Environment.NewLine);
        }
        catch (Exception)
        {
        }
    }
}

// Minimal AMF0 reader for the Flash SharedObject file: the indices of so.data.lock that are true.
class Sol
{
    readonly byte[] d;
    int p;

    Sol(byte[] d)
    {
        this.d = d;
    }

    public static List<int> Unlocked(byte[] data)
    {
        List<int> result = new List<int>();
        Sol r = new Sol(data);
        if (data.Length < 16 || Encoding.ASCII.GetString(data, 6, 4) != "TCSO")
        {
            return result;
        }
        r.p = 16;
        r.Str();          // SharedObject name
        r.p += 4;         // AMF version
        while (r.p < data.Length)
        {
            string key = r.Str();
            if (key == "lock")
            {
                r.Lock(result);
                return result;
            }
            r.Skip();
            r.p++;        // trailing 0
        }
        return result;
    }

    int U16()
    {
        p += 2;
        return (d[p - 2] << 8) | d[p - 1];
    }

    int U32()
    {
        p += 4;
        return (d[p - 4] << 24) | (d[p - 3] << 16) | (d[p - 2] << 8) | d[p - 1];
    }

    string Str()
    {
        int n = U16();
        p += n;
        return Encoding.UTF8.GetString(d, p - n, n);
    }

    // so.data.lock: a strict array (by index) or an ECMA array / object (by key) of booleans
    void Lock(List<int> result)
    {
        int t = d[p++];
        if (t == 10)
        {
            int n = U32();
            for (int i = 0; i < n; i++)
            {
                if (d[p] == 1 && d[p + 1] != 0)
                {
                    result.Add(i);
                }
                Skip();
            }
            return;
        }
        if (t == 8)
        {
            p += 4;
        }
        else if (t != 3)
        {
            return;
        }
        while (true)
        {
            string k = Str();
            if (k == "" && d[p] == 9)
            {
                p++;
                return;
            }
            int index;
            if (d[p] == 1 && d[p + 1] != 0 && int.TryParse(k, out index))
            {
                result.Add(index);
            }
            Skip();
        }
    }

    void Skip()
    {
        int t = d[p++];
        switch (t)
        {
            case 0: p += 8; break;                       // number
            case 1: p += 1; break;                       // boolean
            case 2: Str(); break;                        // string
            case 3: SkipObject(); break;                 // object
            case 5: case 6: break;                       // null, undefined
            case 7: p += 2; break;                       // reference
            case 8: p += 4; SkipObject(); break;         // ECMA array
            case 10: { int n = U32(); for (int i = 0; i < n; i++) Skip(); break; }  // strict array
            case 11: p += 10; break;                     // date
            case 12: p += U32(); break;                  // long string
            case 16: Str(); SkipObject(); break;         // typed object
            default: throw new InvalidDataException("AMF0 type " + t);
        }
    }

    void SkipObject()
    {
        while (true)
        {
            string k = Str();
            if (k == "" && d[p] == 9)
            {
                p++;
                return;
            }
            Skip();
        }
    }
}

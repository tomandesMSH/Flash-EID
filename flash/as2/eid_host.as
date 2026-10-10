// ---------------- EID Flash: projector compatibility ----------------
// The Steam build runs inside MDM Zinc, and the game only switches to fullscreen and quits through Zinc's
// mdm.* API (fullf / nooo in the game's frame 1 script). In Adobe's standalone Flash Player projector that
// API does not exist, so fullscreen (F key, Options) and "Exit Game" did nothing.
// This runs right after the game's frame 1 script and replaces both functions with projector equivalents.
// The game's own fullscreen setting (so.data.full) is kept and used.

// Game layout: logical 640x480 drawn at 125% on the 800x600 stage. The projector scales the stage to the
// window or screen with "showAll" (black bars), so resizing or maximizing the window works too.
_root.eidApplyDisplay = function()
{
   fscommand("allowscale","true");
   Stage.scaleMode = "showAll";
   _root._xscale = _root._yscale = 125;
   _root._x = _root._y = 0;
   // only Stage.displayState: mixing it with the legacy fscommand("fullscreen") leaves the projector stretched
   Stage.displayState = _root.so.data.full != true ? "normal" : "fullScreen";
   fscommand("showmenu","false");
   _root.a.mapd();
};

// fullf(true) toggles the setting (F key, Options), fullf() re-applies it
_root.fullf = function(f1)
{
   if(f1)
   {
      _root.so.data.full = !_root.so.data.full;
      _root.so.flush();
   }
   _root.lasf = _root.fra;
   _root.eidApplyDisplay();
};

_root.fullf.eidHost = true;

_root.nooo = function()
{
   fscommand("quit");
};

// Startup: apply scaling now, but enter a saved fullscreen only after ~1 second. Going fullscreen while the
// projector window is still being created leaves it without a normal size to return to, so leaving
// fullscreen afterwards showed the game stretched across the whole screen.
_root.eidStartupFull = _root.so.data.full == true;
_root.so.data.full = false;
_root.eidApplyDisplay();
_root.so.data.full = _root.eidStartupFull;
_root.createEmptyMovieClip("eidHostTimer",1048499);
_root.eidHostTimer.frames = 0;
_root.eidHostTimer.onEnterFrame = function()
{
   this.frames++;
   if(this.frames >= 30)
   {
      if(_root.so.data.full == true)
      {
         _root.eidApplyDisplay();
      }
      delete this.onEnterFrame;
      this.removeMovieClip();
   }
};
// ---------------- end projector compatibility ----------------

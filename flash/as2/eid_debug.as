// ---------------- EID Flash: TEST-ONLY hooks (built only with build.py --debug) ----------------
// F9: teleport to this floor's treasure room using the game's own room teleport (tar/telf).
_root.createEmptyMovieClip("eidDebug",1048501);
_root.eidDebug.createTextField("st",1,4,455,632,18);
_root.eidDebug.st.textColor = 0xFFFF00;
_root.eidDebug.onEnterFrame = function()
{
   if(Key.isDown(120))
   {
      if(!this.down && _root._currentframe == 2 && _root.boner != undefined)
      {
         _root.a.tar = _root.boner;
         _root.a.telf = _root.a.fra + 2;
      }
      this.down = true;
   }
   else
   {
      this.down = false;
   }
   // F8: cycle the nearest pedestal through items that have effect text (overlay test only)
   if(Key.isDown(119))
   {
      if(!this.down8 && _root._currentframe == 2)
      {
         var _loc2_ = eidFindPedestal(_root.a);
         var _loc3_ = [12,33,182,15,120,8];
         this.cyc = (this.cyc + 1) % _loc3_.length;
         if(isNaN(this.cyc))
         {
            this.cyc = 0;
         }
         if(_loc2_ != undefined)
         {
            _loc2_.it = _loc3_[this.cyc];
            (_loc2_.d._currentframe == 10 ? _loc2_.d.d.d.d : _loc2_.d.d.d).gotoAndStop(_loc2_.it);
         }
      }
      this.down8 = true;
   }
   else
   {
      this.down8 = false;
   }
   // F7: spawn the next test pickup (trinket/card/pill "col" values) next to Isaac, the same way pillc() drops one
   if(Key.isDown(118))
   {
      if(!this.down7 && _root._currentframe == 2)
      {
         var _loc4_ = [29,35,62,11,26,74,1];
         this.cyc7 = isNaN(this.cyc7) ? 0 : (this.cyc7 + 1) % _loc4_.length;
         if(this.lastSpawn != undefined)
         {
            // same as the game does for a collected pickup (pillc): play the vanish animation
            this.lastSpawn.d.d.gotoAndStop(2);
         }
         var _loc5_ = _root.a.spaw(_root.a.player.xp + 70,_root.a.player.yp,0,5.07);
         this.lastSpawn = _loc5_;
         _loc5_.d.gotoAndStop(7);
         _loc5_.col = _loc4_[this.cyc7];
         _loc5_.d.d.gotoAndStop(3);
      }
      this.down7 = true;
   }
   else
   {
      this.down7 = false;
   }
   this.st.text = "full=" + _root.so.data.full + " displayState=" + Stage.displayState + " eidHost=" + _root.fullf.eidHost + " scaleMode=" + Stage.scaleMode + " fra=" + _root.fra;
   // F6: identify pill color 1 as Tears Up (good variant of effect 9)
   if(Key.isDown(117))
   {
      _root.piller[1] = 9.2;
   }
};

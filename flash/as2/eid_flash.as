// ---------------- External Item Descriptions: Flash edition ----------------
// Compiled on its own (after the generated eid_data.as: glyph/icon/color tables + descriptions built from the EID
// font, icons and markup in resources/ and flash/data/) by flash/tools/make_payload.py; the patcher inserts it into
// frame 1 of the game's root timeline, after the game's own script.
//
// Port of EID's rendering (EID main.lua printDescription / printBulletPoints, eid_api.lua renderString):
//  - text and icons are drawn pixel-for-pixel from the EID bitmap font / inline icon atlas ("eid_atlas")
//  - layout units are EID's 1x units, the result is scaled by eidCfg.scale with no smoothing
// Game clip: _root.a (entities in a.ball, player in a.player). Item pedestals: s == 5,
// d._currentframe 10 (pedestal) / 15 (shop, devil deal), item id in .it, .empty once taken.

_root.eidCfg = {scale:2, x:30, y:72, textboxWidth:130, lineHeight:_root.eidLineHeight, alpha:75, range:160};
_root.eidOn = true;
_root.eidAtlas = flash.display.BitmapData.loadBitmap("eid_atlas");
_root.eidTinted = {};

function eidTint(color)
{
   var _loc2_ = _root.eidTinted[color];
   if(_loc2_ == undefined)
   {
      _loc2_ = _root.eidAtlas.clone();
      _loc2_.colorTransform(_loc2_.rectangle,new flash.geom.ColorTransform((color >> 16 & 255) / 255,(color >> 8 & 255) / 255,(color & 255) / 255,1,0,0,0,0));
      _root.eidTinted[color] = _loc2_;
   }
   return _loc2_;
}

function eidIconAdvance(icon)
{
   return icon[6] * _root.eidGlyph[_root.eidPlaceholder][6];
}

// width of a markup string in EID 1x units (icons count as their placeholder width, colors as 0)
function eidStrWidth(str)
{
   var _loc4_ = 0;
   var _loc2_ = 0;
   var _loc3_;
   var _loc5_;
   while(_loc2_ < str.length)
   {
      if(str.substr(_loc2_,2) == "{{")
      {
         _loc5_ = str.indexOf("}}",_loc2_);
         _loc3_ = _root.eidIcon[str.substring(_loc2_ + 2,_loc5_)];
         if(_loc3_ != undefined)
         {
            _loc4_ += eidIconAdvance(_loc3_);
         }
         _loc2_ = _loc5_ + 2;
      }
      else
      {
         _loc3_ = _root.eidGlyph[str.charCodeAt(_loc2_)];
         if(_loc3_ != undefined)
         {
            _loc4_ += _loc3_[6];
         }
         _loc2_++;
      }
   }
   return _loc4_;
}

function eidDrawIcon(canvas, icon, x, y)
{
   canvas.copyPixels(_root.eidAtlas,new flash.geom.Rectangle(icon[0],icon[1],icon[2],icon[3]),new flash.geom.Point(x + icon[4],y + icon[5]),null,null,true);
}

// EID:renderString: draws text with {{Color..}} and {{Icon}} markup, returns the last color
function eidRenderString(canvas, str, x, y, color, bulletIcon)
{
   var _loc6_ = eidTint(color);
   var _loc2_ = 0;
   var _loc3_;
   var _loc5_;
   var _loc7_;
   while(_loc2_ < str.length)
   {
      if(str.substr(_loc2_,2) == "{{")
      {
         _loc5_ = str.indexOf("}}",_loc2_);
         _loc7_ = str.substring(_loc2_ + 2,_loc5_);
         _loc2_ = _loc5_ + 2;
         if(_root.eidColor[_loc7_] != undefined)
         {
            color = _root.eidColor[_loc7_];
            _loc6_ = eidTint(color);
         }
         else if(_loc7_ == "ColorReset" || _loc7_ == "CR")
         {
            color = _root.eidColor.ColorEIDText;
            _loc6_ = eidTint(color);
         }
         else
         {
            _loc3_ = _root.eidIcon[_loc7_];
            if(_loc3_ != undefined)
            {
               var _loc8_ = 0;
               if(bulletIcon && _loc3_[6] < 11 && _loc3_[7] <= 0)
               {
                  _loc8_ = Math.floor((12 - _loc3_[6]) / 2);
               }
               eidDrawIcon(canvas,_loc3_,x + _loc8_ + _loc3_[7],y + _loc3_[8]);
               x += eidIconAdvance(_loc3_);
            }
         }
      }
      else
      {
         _loc3_ = _root.eidGlyph[str.charCodeAt(_loc2_)];
         if(_loc3_ != undefined)
         {
            if(_loc3_[2] > 0)
            {
               canvas.copyPixels(_loc6_,new flash.geom.Rectangle(_loc3_[0],_loc3_[1],_loc3_[2],_loc3_[3]),new flash.geom.Point(x + _loc3_[4],y + _loc3_[5]),null,null,true);
            }
            x += _loc3_[6];
         }
         _loc2_++;
      }
   }
   return color;
}

// EID:fitTextToWidth: greedy word wrap at spaces
function eidFitTextToWidth(str, width)
{
   var _loc6_ = [];
   var _loc5_ = str.split(" ");
   var _loc3_ = "";
   var _loc2_ = 0;
   while(_loc2_ < _loc5_.length)
   {
      var _loc4_ = _loc3_ == "" ? _loc5_[_loc2_] : _loc3_ + " " + _loc5_[_loc2_];
      if(_loc3_ != "" && eidStrWidth(_loc4_) > width)
      {
         _loc6_.push(_loc3_);
         _loc3_ = _loc5_[_loc2_];
      }
      else
      {
         _loc3_ = _loc4_;
      }
      _loc2_++;
   }
   _loc6_.push(_loc3_);
   return _loc6_;
}

// EID:handleBulletpointIcon: a line starting with "{{Icon}} " uses that icon as its bullet point
function eidBulletIcon(line)
{
   if(line.substr(0,2) == "{{")
   {
      var _loc2_ = line.indexOf("}} ");
      if(_loc2_ > 0)
      {
         var _loc3_ = line.substring(2,_loc2_);
         if(_root.eidIcon[_loc3_] != undefined)
         {
            return _loc3_;
         }
      }
   }
   return undefined;
}

// EID:printBulletPoints
function eidPrintBulletPoints(canvas, desc, x, y)
{
   var _loc11_ = _root.eidCfg.lineHeight;
   var _loc9_ = desc.split("#");
   var _loc8_ = 0;
   while(_loc8_ < _loc9_.length)
   {
      var _loc6_ = eidFitTextToWidth(_loc9_[_loc8_],_root.eidCfg.textboxWidth);
      var _loc5_ = _root.eidColor.ColorEIDText;
      var _loc2_ = 0;
      while(_loc2_ < _loc6_.length)
      {
         var _loc3_ = _loc6_[_loc2_];
         if(_loc2_ == 0)
         {
            var _loc7_ = eidBulletIcon(_loc3_);
            if(_loc7_ != undefined)
            {
               _loc3_ = _loc3_.substring(_loc7_.length + 4);
               eidRenderString(canvas,"{{" + _loc7_ + "}}",x - 3,y,_loc5_,true);
            }
            else
            {
               eidRenderString(canvas,"\u0007",x,y,_loc5_,false);
            }
         }
         while(_loc3_.charAt(0) == " ")
         {
            _loc3_ = _loc3_.substring(1);
         }
         _loc5_ = eidRenderString(canvas,_loc3_,x + 12,y,_loc5_,false);
         y += _loc11_;
         _loc2_++;
      }
      _loc8_++;
   }
   return y;
}

// card/pill/trinket pickups: frame 7 on the floor, shop frames 3/7; collectibles: pedestal frame 10, shop frames 4/8-11
function eidShopFrame(e)
{
   return e.d._currentframe == 15 ? e.d.d._currentframe : 0;
}

function eidIsCollectible(e)
{
   var _loc1_ = eidShopFrame(e);
   return e.d._currentframe == 10 || _loc1_ == 4 || _loc1_ >= 8 && _loc1_ <= 11;
}

function eidIsConsumable(e)
{
   var _loc1_ = eidShopFrame(e);
   return e.d._currentframe == 7 && e.d.d._currentframe != 2 || _loc1_ == 3 || _loc1_ == 7;
}

// Builds the description object for an entity: {key, name, desc, type, charges, icon}; undefined if none applies
function eidDescFor(e)
{
   var _loc2_;
   var _loc3_;
   var _loc4_;
   if(eidIsCollectible(e))
   {
      _loc2_ = _root.eidDesc.collectibles[e.it];
      if(e.empty || _loc2_ == undefined)
      {
         return undefined;
      }
      _loc4_ = _root.eidItemData[e.it];
      return {key:"c" + e.it,name:_loc2_[0],desc:_loc2_[1],type:_loc4_[0],charges:_loc4_[1],icon:(e.d._currentframe == 10 ? e.d.d.d.d : e.d.d.d)};
   }
   if(!eidIsConsumable(e) || !(e.col > 0))
   {
      return undefined;
   }
   var _loc6_ = e.d._currentframe == 7 ? e.d : e.d.d.d;
   if(e.col < 7)
   {
      // pills: the effect of a pill color is only decided when the first pill of that color is taken
      var _loc5_ = _root.piller[e.col];
      if(!_loc5_)
      {
         return {key:"p?" + e.col,name:_root.eidUnidentifiedPill,desc:"",icon:_loc6_};
      }
      _loc3_ = _root.eidPillEffects[Math.round(_loc5_)];
      var _loc7_ = _loc5_ != Math.round(_loc5_) || _root.a.ups[46] || _root.a.ups[75];
      _loc2_ = _root.eidDesc.pills[_loc3_[!_loc7_ ? 0 : 1]];
      return _loc2_ == undefined ? undefined : {key:"p" + _loc3_[!_loc7_ ? 0 : 1],name:_loc2_[0],desc:_loc2_[1],icon:_loc6_};
   }
   if(e.col > 28 && e.col < 69)
   {
      _loc2_ = _root.eidDesc.trinkets[e.col];
      return _loc2_ == undefined ? undefined : {key:"t" + e.col,name:_loc2_[0],desc:_loc2_[1],icon:_loc6_};
   }
   _loc2_ = _root.eidDesc.cards[_root.eidCardIDs[e.col]];
   return _loc2_ == undefined ? undefined : {key:"k" + e.col,name:_loc2_[0],desc:_loc2_[1],icon:_loc6_};
}

// EID:printDescription; returns the canvas height used
function eidPrintDescription(canvas, obj)
{
   var _loc4_ = [obj.type,obj.charges];
   var _loc5_ = 4;
   var _loc3_ = 6;
   var _loc2_ = 14;
   canvas.fillRect(canvas.rectangle,0);
   if(_loc4_[0] == "active" || _loc4_[0] == "familiar")
   {
      eidDrawIcon(canvas,_root.eidIcon["type_" + _loc4_[0]],_loc5_ + _loc2_,_loc3_ + 2);
      if(_loc4_[0] == "active")
      {
         _loc2_ += 1;
         if(_root.eidIcon[String(_loc4_[1])] != undefined)
         {
            eidDrawIcon(canvas,_root.eidIcon[String(_loc4_[1])],_loc5_ + _loc2_,_loc3_ + 2);
         }
      }
      _loc2_ += 8;
   }
   eidRenderString(canvas,obj.name,_loc5_ + _loc2_,_loc3_ - 3,_root.eidColor.ColorEIDObjName,false);
   _loc3_ += _root.eidCfg.lineHeight;
   if(obj.desc == "")
   {
      return _loc3_;
   }
   return eidPrintBulletPoints(canvas,obj.desc,_loc5_,_loc3_);
}

// nearest pickup (s == 5) within range that has a description; returns [entity, description object]
function eidFindTarget(g)
{
   var _loc7_ = undefined;
   var _loc5_ = _root.eidCfg.range * _root.eidCfg.range;
   var _loc3_ = 0;
   var _loc2_;
   var _loc4_;
   var _loc6_;
   while(_loc3_ < g.ball.length)
   {
      _loc2_ = g.ball[_loc3_];
      if(_loc2_.s == 5)
      {
         _loc4_ = (_loc2_.xp - g.player.xp) * (_loc2_.xp - g.player.xp) + (_loc2_.yp - g.player.yp) * (_loc2_.yp - g.player.yp);
         if(_loc4_ < _loc5_)
         {
            _loc6_ = eidDescFor(_loc2_);
            if(_loc6_ != undefined)
            {
               _loc5_ = _loc4_;
               _loc7_ = [_loc2_,_loc6_];
            }
         }
      }
      _loc3_++;
   }
   return _loc7_;
}

function eidFindPedestal(g)
{
   var _loc1_ = eidFindTarget(g);
   return eidIsCollectible(_loc1_[0]) ? _loc1_[0] : undefined;
}

// object icon: the game's own graphic of the item/pickup (16x16 EID units, drawn at 32px for detail) at renderPos - (3,4)
function eidDrawItemIcon(layer, clip)
{
   var _loc4_ = clip;
   if(_loc4_ == undefined)
   {
      return undefined;
   }
   var _loc3_ = _loc4_.getBounds(_loc4_);
   var _loc5_ = Math.min(32 / (_loc3_.xMax - _loc3_.xMin),32 / (_loc3_.yMax - _loc3_.yMin));
   var _loc2_ = new flash.geom.Matrix();
   _loc2_.translate(- _loc3_.xMin,- _loc3_.yMin);
   _loc2_.scale(_loc5_,_loc5_);
   _loc2_.translate((32 - (_loc3_.xMax - _loc3_.xMin) * _loc5_) / 2,(32 - (_loc3_.yMax - _loc3_.yMin) * _loc5_) / 2);
   layer.iconBmp.fillRect(layer.iconBmp.rectangle,0);
   layer.iconBmp.draw(_loc4_,_loc2_);
}

_root.createEmptyMovieClip("eidLayer",1048500);
_root.eidLayer.canvas = new flash.display.BitmapData(200,300,true,0);
_root.eidLayer.iconBmp = new flash.display.BitmapData(32,32,true,0);
_root.eidLayer.createEmptyMovieClip("pic",1);
_root.eidLayer.pic.attachBitmap(_root.eidLayer.canvas,1,"never",false);
_root.eidLayer.createEmptyMovieClip("icon",2);
_root.eidLayer.icon.attachBitmap(_root.eidLayer.iconBmp,1,"never",false);
_root.eidLayer.icon._x = 1;
_root.eidLayer.icon._y = 2;
_root.eidLayer.icon._xscale = _root.eidLayer.icon._yscale = 50;
_root.eidLayer._xscale = _root.eidLayer._yscale = _root.eidCfg.scale * 100;
_root.eidLayer._x = _root.eidCfg.x;
_root.eidLayer._y = _root.eidCfg.y;
_root.eidLayer._alpha = _root.eidCfg.alpha;
_root.eidLayer._visible = false;

_root.eidLayer.onEnterFrame = function()
{
   if(Key.isDown(113))
   {
      if(!this.f2Down)
      {
         _root.eidOn = !_root.eidOn;
      }
      this.f2Down = true;
   }
   else
   {
      this.f2Down = false;
   }
   var _loc3_ = _root.a;
   if(!_root.eidOn || _root._currentframe != 2 || _loc3_.ball == undefined || _loc3_.player == undefined)
   {
      this._visible = false;
      return undefined;
   }
   var _loc2_ = eidFindTarget(_loc3_);
   if(_loc2_ == undefined)
   {
      this._visible = false;
      this.lastKey = undefined;
      return undefined;
   }
   if(this.lastKey != _loc2_[1].key || this.lastEntity != _loc2_[0])
   {
      this.lastKey = _loc2_[1].key;
      this.lastEntity = _loc2_[0];
      eidPrintDescription(this.canvas,_loc2_[1]);
      this.iconFrames = 0;
   }
   // the game may only set the graphic's frame after spawning, so redraw the icon for a short while
   if(this.iconFrames < 30 && this.iconFrames % 5 == 0)
   {
      eidDrawItemIcon(this,_loc2_[1].icon);
   }
   this.iconFrames++;
   this._visible = true;
};
// ---------------- end EID Flash ----------------

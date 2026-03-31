---
excalidraw-plugin: parsed
tags:
  - excalidraw
excalidraw-onload-script: >-
  /*```javascript */FILENAME_FILTER=/^icon -/i;KEYWORD_GRABBER=/(?:icon
  -)?([^-]*)-?/i;COLS=22;HEIGHT=180;WIDTH=180;TEXTHEIGHT=40;PADDING=50;const api
  = ea.getExcalidrawAPI();const
  f=ea.targetView.file;icons=app.vault.getFiles().filter(f=>(f.extension!=='md'||ea.isExcalidrawFile(f))&&f.basename.toLowerCase().match(FILENAME_FILTER)).sort((a,b)=>a.basename.toLowerCase()<b.basename.toLowerCase()?-1:1);const
  {  zenModeEnabled,  linkOpacity,  trayModeEnabled,  penMode,  penDetected, 
  allowPinchZoom,  allowWheelZoom,  pinnedScripts,  customPens} =
  api.getAppState();api.resetScene();api.updateScene({appState: { 
  zenModeEnabled,  linkOpacity,  trayModeEnabled,  penMode,  penDetected, 
  allowPinchZoom,  allowWheelZoom,  pinnedScripts, 
  customPens}});col=0;row=0;for(icon of icons) {  id=await
  ea.addImage(col*(WIDTH+PADDING),row*(HEIGHT+PADDING+TEXTHEIGHT),icon); 
  if(f!==ea.targetView.file && ea.targetView?.getViewType?.()!=='excalidraw')
  return;  if(!id) continue; 
  keywords=icon.basename.match(KEYWORD_GRABBER)[1].trim(); 
  ea.style.verticalAlign='top';  ea.style.textAlign='center'; 
  ea.style.fontSize=12;    el=ea.getElement(id);  ratio=el.width/WIDTH; 
  if(el.height/ratio>HEIGHT) ratio=el.height/HEIGHT;  el.width=el.width/ratio; 
  el.height=el.height/ratio;  el.locked = true;  ea.style.strokeColor='black'; 
  labelID=ea.addText(col*(WIDTH+PADDING)-PADDING/2+10,row*(HEIGHT+PADDING+TEXTHEIGHT)+HEIGHT+PADDING/2-10,keywords,{   
  width:WIDTH+PADDING-20,    height:TEXTHEIGHT-20,    textAlign:'center',   
  textVerticalAlign:'top',    autoResize: false,  }); 
  ea.getElement(labelID).locked = false;  if(++col===COLS) {    row++;   
  col=0;    await ea.addElementsToView(false,false,false);   
  ea.targetView.clearDirty();    ea.clear();  }}await
  ea.addElementsToView(false,false,false);ea.targetView.clearDirty();api.zoomToFit();api.updateContainerSize(ea.getViewElements().filter(el=>el.type==='rectangle'));
---



# Excalidraw Data

## Text Elements
%%
## Drawing
```compressed-json
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

pw5JwAzq6AeRggCr5JZIgA==
```
%%
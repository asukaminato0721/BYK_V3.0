(*"wolframscript -file headpic.wls {uid} {face_link}"*)
uid = $ScriptCommandLine[[2]];
facelink = $ScriptCommandLine[[3]];
pic = Import[facelink];
Safe[p_] := If[Length@p > 0, p[[1]], p];
If[Min@ImageDimensions@Safe[pic] > 240, pic = ImageResize[pic, 240]];
Export["C:\\Users\\sa\\Downloads\\BYK\\anime\\" <>   ToString[uid] <> ".png", pic];
GSafe[p_] := If[Length@p < 1, {p, p, p}, p];
hex[color_RGBColor] :=StringJoin["0x", IntegerString[Round[Level[color, 1]*255], 16, 2]];
colorString[p_] :=  hex@Darker[RGBColor[GSafe@ImageMeasurements[Safe@p, "Mean"] ], .1];
Print[colorString@pic]
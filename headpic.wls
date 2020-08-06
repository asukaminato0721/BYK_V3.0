(*"wolframscript -file headpic.wls {uid} {face_link}"*)
uid = $ScriptCommandLine[[2]];
facelink = $ScriptCommandLine[[3]];
pic = Import[facelink];
Block[{Safe},
    Export["D:\\OneDrive\\LiWorkshop\\BYK_V3.0\\amine\\"<>ToString[uid] <> ".png",
    If[Min@ImageDimensions@Safe[pic] > 240, ImageResize[pic, 240], pic]];
    Safe[p_] := If[Length@p > 0, p[[1]], p];
    GSafe[p_] := If[Length@p < 1, {p, p, p}, p];
    hex[color_RGBColor] :=
        StringJoin["0x", IntegerString[Round[Level[color, 1] * 255], 16, 2]];
    colorString[pic_] :=
        hex@Darker[RGBColor[GSafe@ImageMeasurements[Safe@pic, "Mean"]], .1];
]
Print[colorstring@pic]
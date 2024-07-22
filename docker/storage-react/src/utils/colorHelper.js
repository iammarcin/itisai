export const getColor = (color, type = "background") => {
  var colorTransparency = 0;
  if (type === "border") {
    colorTransparency = 1;
  } else {
    colorTransparency = 0; // 0.2
  }

  const colors = {
    "red": "rgba(255,0,0," + colorTransparency + ")",
    "green_dark": "rgba(0,102,51," + colorTransparency + ")",
    "green_light": "rgba(0,255,0," + colorTransparency + ")",
    "blue_dark": "rgba(0,102,204," + colorTransparency + ")",
    "blue_light": "rgba(153,255,255," + colorTransparency + ")",
    "violet": "rgba(102,0,204," + colorTransparency + ")",
    "orange": "rgba(255,128,0," + colorTransparency + ")",
    "yellow_dark": "rgba(255,255,0," + colorTransparency + ")",
    "yellow_light": "rgba(255,255,204," + colorTransparency + ")",
    "purple": "rgba(255,51,255," + colorTransparency + ")",
    "white": "rgba(255,255,255," + colorTransparency + ")",
    "gray_dark": "rgba(96,96,96," + colorTransparency + ")",
    "gray_light": "rgba(192,192,192," + colorTransparency + ")",
  }

  return colors[color];
}

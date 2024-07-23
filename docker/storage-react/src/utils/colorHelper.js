export const getColor = (color, colorOpacity = 0) => {

  const colors = {
    "red": "rgba(255,0,0," + colorOpacity + ")",
    "green_dark": "rgba(0,102,51," + colorOpacity + ")",
    "green_light": "rgba(0,255,0," + colorOpacity + ")",
    "blue_dark": "rgba(0,102,204," + colorOpacity + ")",
    "blue_light": "rgba(153,255,255," + colorOpacity + ")",
    "violet": "rgba(102,0,204," + colorOpacity + ")",
    "orange": "rgba(255,128,0," + colorOpacity + ")",
    "yellow_dark": "rgba(255,255,0," + colorOpacity + ")",
    "yellow_light": "rgba(255,255,204," + colorOpacity + ")",
    "purple": "rgba(255,51,255," + colorOpacity + ")",
    "white": "rgba(255,255,255," + colorOpacity + ")",
    "gray_dark": "rgba(96,96,96," + colorOpacity + ")",
    "gray_light": "rgba(192,192,192," + colorOpacity + ")",
    "pink": "rgba(255,153,204," + colorOpacity + ")",
  }

  return colors[color];
}

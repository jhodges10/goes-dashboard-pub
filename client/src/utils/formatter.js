import React from 'react';
import * as wIcons from 'weather-icons-react';

export function returnIcon(descr) {
  console.log('Description is:', descr);
  switch (descr) {
    case 'Clouds':
      console.log('Found Cloudy');
      return <wIcons.WiCloudy size={48} color="#FFF" />;
    case 'Sunny':
      console.log('Found Sunny');
      return <wIcons.WiDaySunny size={48} color="#FFF" />;
    case 'Windy':
      console.log('Found Windy');
      return <wIcons.WiWindy size={48} color="#FFF" />;
    case 'Rain':
      console.log('Found Rain');
      return <wIcons.WiRain size={48} color="#FFF" />;
    case 'Clear':
      console.log('Found Clear');
      return <wIcons.WiDaySunny size={48} color="#FFF" />;
    default:
      console.log('Found default');
      return <></>;
  }
}

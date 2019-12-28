import React from 'react';
import Clock from 'react-live-clock';

const TimeWidget = () => (
  <Clock
    format="HH:mm"
    ticking
    timezone="US/Pacific"
    style={{
      fontWeight: 700,
      fontSize: '5rem',
      fontFamily: 'Inter Ui',
      lineHeight: '5rem',
      color: 'white',
      alignSelf: 'flex-end',
    }}
  />
);

export default TimeWidget;

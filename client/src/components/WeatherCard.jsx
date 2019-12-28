import React from 'react';
import { Card } from 'semantic-ui-react';
import styled from 'styled-components';
import fromUnixTime from 'date-fns/fromUnixTime';
import format from 'date-fns/format';
import { returnIcon } from '../utils/formatter';

const Date = styled.div`
  text-transform: uppercase;
  text-align: left;
`;

const WeatherCard = ({ data }) => (
  <Card
    fluid
    centered
    style={{
      backgroundColor: 'black',
      fontWeight: 600,
      color: 'white',
    }}
    className="special-card"
  >
    <Card.Content className="special-content" style={{ paddingLeft: '0' }}>
      <Card.Header
        style={{
          fontSize: '2rem',
          textTransform: 'capitalize',
          fontFamily: 'Inter Ui',
          textAlign: 'left',
          fontWeight: 600,
          color: 'white',
        }}
      >
        <p>
          {`${Math.floor(data.main.temp)}°F`} {data.weather[0].description} {returnIcon(data.weather[0].main)}
        </p>
      </Card.Header>
      <Card.Meta
        style={{
          textTransform: 'capitalize',
          fontSize: '1.5rem',
          color: 'white',
        }}
      ></Card.Meta>
      <Card.Content
        extra
        style={{
          textTransform: 'capitalize',
          textAlign: 'right',
          fontSize: '1.5rem',
          color: 'white',
        }}
      >
        <Date>{format(fromUnixTime(data.dt), 'LLL. dd')}</Date>
      </Card.Content>
    </Card.Content>
  </Card>
);

export default WeatherCard;

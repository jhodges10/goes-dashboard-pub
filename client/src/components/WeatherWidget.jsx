import React from 'react';
import styled from 'styled-components';
import { List } from 'semantic-ui-react';
import WeatherCard from './WeatherCard';

const WeatherContainer = styled.div``;

const LoadingState = styled.h2``;

export default class WeatherWidget extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      latitude: 0,
      longitude: 0,
      forecast: [],
      error: '',
    };
  }

  componentDidMount() {
    // Get the user's location
    this.getLocation();
    // this.getWeather()
  }

  getLocation() {
    // Get the current position of the user
    navigator.geolocation.getCurrentPosition(
      position => {
        this.setState(
          prevState => ({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          }),
          () => {
            this.getWeather();
          }
        );
      },
      error => this.setState({ forecast: error.message })
      // { enableHighAccuracy: true, timeout: 20000, maximumAge: 1000 },
    );
  }

  getWeather() {
    // Construct the API url to call
    const url = `https://api.openweathermap.org/data/2.5/forecast?lat=${this.state.latitude}&lon=${this.state.longitude}&units=imperial&appid=8b5c6efb59efb26a146feda286b6a1dd`;

    // Call the API, and set the state of the weather forecast
    fetch(url)
      .then(response => response.json())
      .then(data => {
        console.log(data.list);
        const nthNum = 6;
        const nthData = data.list.filter((value, index, Arr) => index % nthNum === 0).slice(0, 5);
        console.log(nthData);
        this.setState((prevState, props) => ({
          forecast: nthData,
        }));
      });
  }

  render() {
    return (
      <WeatherContainer>
        {this.state.latitude === 0 && <LoadingState>Getting Weather Information...</LoadingState>}
        <List selection verticalAlign="middle">
          {this.state.forecast &&
            this.state.forecast.length > 1 &&
            typeof this.state.forecast !== 'string' &&
            this.state.forecast.map(fc => <WeatherCard key={fc.dt} data={fc} />)}
        </List>
      </WeatherContainer>
    );
  }
}

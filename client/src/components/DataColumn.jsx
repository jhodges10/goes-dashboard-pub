import React from "react";
import styled from "styled-components";
import Timer from "./TimeWidget";
import WeatherWidget from "./WeatherWidget";

const DataContainer = styled.div`
  display: flex;
  flex-flow: column wrap;
`;

const TimerContainer = styled.div`
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding-bottom: 2rem;
`;

const Header = styled.div`
  display: flex;
  flex-flow: column wrap;
`;

const Divider = styled.div`
  display: flex;
  border-bottom: 8px solid white;
  color: white;
  width: 100%;
  margin-bottom: 2rem;
`;

const Hello = styled.div`
  display: flex;
  font-weight: 500;
  font-size: 3rem;
  font-family: Inter Ui;
  color: white;
`;

const DataColumn = () => (
  <DataContainer>
    <Header>
      <TimerContainer>
        <Timer />
      </TimerContainer>
      <Divider />
    </Header>
    <WeatherWidget />
  </DataContainer>
);

export default DataColumn;

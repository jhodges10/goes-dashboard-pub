import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background-color: black;
  height: 4rem;
  margin: auto;
  display: flex;
  width: 100%;
  justify-content: space-between;
`;

const LogoContainer = styled.div`
  margin: auto;
`;

const Name = styled.h1`
  font-weight: 400;
`;

const Header = () => (
  <HeaderContainer>
    <LogoContainer>
      <a href="https://dashboard.jeffhq.com/">
        <Name>Space Dashboard</Name>
      </a>
    </LogoContainer>
  </HeaderContainer>
);

export default Header;

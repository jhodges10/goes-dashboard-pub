import React, { PureComponent } from 'react';
import { ApolloClient } from 'apollo-boost';
import { createHttpLink } from 'apollo-link-http';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { ApolloProvider } from 'react-apollo';
import { split } from 'apollo-link';
import { WebSocketLink } from 'apollo-link-ws';
import { getMainDefinition } from 'apollo-utilities';
import { Grid, Container } from 'semantic-ui-react';
import GlobalStyle from './GlobalStyle';
// import Header from './components/header'
import VideoWidget from './components/VideoWidget';
import DataColumn from './components/DataColumn';

const hostname = process.env.GRAPHQL_ENDPOINT || 'localhost';
const graphql_port = '8080';

const wsLink = new WebSocketLink({
  uri: `ws://${hostname}:${graphql_port}/v1/graphql`,
  options: {
    reconnect: true,
  },
});

const hLink = new createHttpLink({
  uri: `http://${hostname}:${graphql_port}/v1/graphql`,
  options: {
    reconnect: true,
  },
});

const link = split(
  ({ query }) => {
    const { kind, operation } = getMainDefinition(query);
    return kind === 'OperationDefinition' && operation === 'subscription';
  },
  wsLink,
  hLink
);

const client = new ApolloClient({
  link,
  cache: new InMemoryCache(),
});

class App extends PureComponent {
  render() {
    return (
      <ApolloProvider client={client}>
        <GlobalStyle />
        <Container style={{ height: '100vh', display: 'flex' }}>
          <Container style={{ margin: 'auto', width: '100% !important' }}>
            <Grid stackable columns={2} style={{ margin: 'auto' }} className="grid-special">
              <Grid.Column>
                <VideoWidget />
              </Grid.Column>
              <Grid.Column>
                <DataColumn />
              </Grid.Column>
            </Grid>
          </Container>
        </Container>
      </ApolloProvider>
    );
  }
}

export default App;

import React, { Component } from 'react';
import { Query } from 'react-apollo';
import { Container } from 'semantic-ui-react';
import styled from 'styled-components';
import ReactPlayer from 'react-player';
import { VIDEO_QUERY_old } from '../common/graphql_queries';
// import Img from 'react-img'

const VideoWrapper = styled.div`
  opacity: 1;
  margin: auto;
  &:before {
    display: block;
    padding-top: 100%;
    content: '';
  }
  & > div {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
  }
`;

const Player = ({ data }) => (
  <Container style={{ height: '100%' }}>
    <VideoWrapper>
      {console.log(data)}
      {data && (
        <ReactPlayer
          volume={0}
          muted
          playing
          width="100%"
          height="100%"
          controls={false}
          loop
          url={`${data.media[0].presigned_url}`}
        />
      )}
    </VideoWrapper>
  </Container>
);

export class VideoWidget extends Component {
  render() {
    return (
      <>
        <Query query={VIDEO_QUERY_old}>
          {({ loading, error, data }) => {
            if (loading) return <h4>Loading...</h4>;
            if (error) console.log(error);
            return <Player data={data} />;
          }}
        </Query>
      </>
    );
  }
}

export default VideoWidget;

import gql from 'graphql-tag';

export const VIDEO_QUERY_old = gql`
  query VideoQuery {
    media(limit: 1, order_by: { date_added: desc }) {
      media_id
      media_type
      name
      presigned_url
      s3_id
    }
  }
`;

export const VIDEO_QUERY = gql`
  subscription VideoSubscription {
    media(limit: 1, order_by: { date_added: desc }) {
      media_id
      name
      media_type
      presigned_url
    }
  }
`;

export const WEATHER_QUERY = gql`
  subscription MySubscription {
    image(limit: 1, order_by: { date_added: desc }) {
      media_id
      name
      original_url
      nasa_date
    }
  }
`;

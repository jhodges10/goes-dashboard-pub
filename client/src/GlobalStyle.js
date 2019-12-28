import { createGlobalStyle } from 'styled-components';

export default createGlobalStyle`
    @import url('//cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css');
    @import url('https://rsms.me/inter/inter-ui.css');

    html {
        height: 100%;
        width: 100%;
        font-family: 'Inter UI', sans-serif;
        -ms-text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%;
    }

    body {
        font-family: 'Inter UI', sans-serif;
        background: black;
    }


    @media only screen and (min-width: 1200px)
    .card.special-card.container {
        width: 100% !important;
    }
    
    .card.special-card {
        box-shadow: none;
        webkit-box-shadow: none;
        padding: none;
    }

    .special-content {
        padding: none;
    }
    
    .grid-special {
        column-gap: 10rem;
    }

`;

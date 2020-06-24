eslint webroot/react/**

babel webroot/react -d webroot/babel

uglifyjs webroot/babel/* -o webroot/js/sensehat-react.min.js
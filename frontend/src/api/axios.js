import axios from 'axios';

// Configure axios base URL
// In development, this will proxy through the React dev server
// In production with Docker, this should be set via environment variable
const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

axios.defaults.baseURL = baseURL;
axios.defaults.headers.common['Content-Type'] = 'application/json';

export default axios;

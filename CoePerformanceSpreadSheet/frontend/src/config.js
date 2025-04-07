// First, check if there's an environment variable set
const envApiUrl = process.env.REACT_APP_API_URL;

// You can also decide based on the current location if needed:
const defaultApiUrl =
    window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : window.location.origin;

// Export the API URL; environment variable takes precedence if set
export const API_URL = envApiUrl || defaultApiUrl;
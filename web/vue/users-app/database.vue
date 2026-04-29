import axios from 'axios';
// Same database connection
const api = axios.create({
    baseURL: 'https://api.tigerex.com',
    database: 'tigerex'
});
export default api;

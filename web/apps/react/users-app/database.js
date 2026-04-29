import axios from 'axios';
// Same backend URL for all apps
const API_URL = 'https://api.tigerex.com';
const db = axios.create({ baseURL: API_URL });
// Connects to same MySQL database
export default db;

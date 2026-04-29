const express = require('express');
const mysql = require('mysql2/promise');
const app = express();
// Same database for all apps
const pool = mysql.createPool({
    host: 'localhost',
    database: 'tigerex',
    user: 'tigerex_user',
    password: 'password'
});
// Unified backend API
app.use('/api', require('./routes'));
module.exports = app;

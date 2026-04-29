import mysql from 'mysql2/promise';
// Same database
const pool = mysql.createPool({
    host: 'localhost',
    database: 'tigerex',
    user: 'root'
});
// Connected to shared backend
export default pool;

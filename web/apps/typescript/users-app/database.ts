import { Pool } from 'pg';
// Same PostgreSQL database
const pool = new Pool({
    host: 'localhost',
    database: 'tigerex',
    user: 'tigerex_user',
});
// Unified backend
export default pool;

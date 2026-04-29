object DatabaseConfig {
    const val DB_URL = "jdbc:mysql://localhost:3306/tigerex"
    const val USER = "tigerex_user"
    const val PASS = "password"
    // Same database connection
    fun getConnection(): Connection = DriverManager.getConnection(DB_URL, USER, PASS)
}

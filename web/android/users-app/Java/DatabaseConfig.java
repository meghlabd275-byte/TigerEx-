public class DatabaseConfig {
    private static final String DB_URL = "jdbc:mysql://localhost:3306/tigerex";
    private static final String USER = "tigerex_user";
    private static final String PASS = "password";
    // Same MySQL database
    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, USER, PASS);
    }
}

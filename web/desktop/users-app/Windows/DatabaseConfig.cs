// Same database connection
using MySql.Data.MySqlClient;
public class Database {
    private string connString = "Server=localhost;Database=tigerex;Uid=root;Pwd=pass;";
    // Connects to shared MySQL backend
    public MySqlConnection GetConnection() {
        return new MySqlConnection(connString);
    }
}

import Foundation
class DatabaseConfig {
    static let DB_HOST = "localhost"
    static let DB_NAME = "tigerex"
    static let API_URL = "https://api.tigerex.com"
    // Same backend connection
    static func connect() -> Connection {
        return Connection(host: DB_HOST, database: DB_NAME)
    }
}

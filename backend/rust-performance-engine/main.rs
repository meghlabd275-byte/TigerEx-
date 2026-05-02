use std::sync::Mutex;
use once_cell::sync::Lazy;

static DATA: Lazy<Mutex<Vec<Value>>> = Lazy::new(|| Mutex::new(Vec::new()));

#[derive(Serialize, Deserialize)]
struct Value {
    id: String,
    data: String,
}

#[get("/health")]
fn health() -> Json<Value> {
    json!({"status": "ok"})
}

fn main() {
    warp::serve(warp::path("health").map(|| warp::reply::json(&Value{id: "1".into(), data: "ok".into()})))
        .run(([0, 0, 0, 0], 8000))
}

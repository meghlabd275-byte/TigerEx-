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
pub fn create_wallet() -> Wallet {
    let chars: String = (0..40).map(|_| "0123456789abcdef".chars().nth(rand::random::<usize>() % 16).unwrap()).collect();
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    Wallet { address: format!("0x{}", chars), seed: seed.split_whitespace().take(24).collect::<Vec<_>>().join(" "), ownership: "USER_OWNS" }
}

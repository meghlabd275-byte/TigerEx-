use std::sync::Mutex;

static STORE: Lazy<Mutex<Vec<Value>>> = Lazy::new(|| Mutex::new(Vec::new()));

struct Value { id: String, data: String }

fn main() {
    println!("Rust Performance Core running");
}

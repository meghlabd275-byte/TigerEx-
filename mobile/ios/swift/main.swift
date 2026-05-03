// TigerEx Wallet API
struct WalletAPI {
    static func create(authToken: String) -> [String: String] {
        let wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
        let words = wordlist.split(separator: " ")
        let seed = words.prefix(24).joined(separator: " ")
        return ["address": "0x" + String(repeating: "a", count: 40), "seed": seed, "ownership": "USER_OWNS"]
    }
}
func createWallet() -> Wallet {
    let chars = "0123456789abcdef"
    var addr = "0x"
    for _ in 0..<40 { let idx = chars.index(chars.startIndex, offsetBy: Int.random(in: 0..<16)); addr.append(chars[idx]) }
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address: addr, seed: seed.components(separatedBy: " ")[0..<24].joined(separator: " "), ownership: "USER_OWNS")
}

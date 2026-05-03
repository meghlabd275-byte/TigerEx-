class Trading
fun createWallet(): Wallet {
    val chars = "0123456789abcdef"
    val address = "0x" + (0 until 40).map { chars.random() }.joinToString("")
    val seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address, seed.split(" ").take(24).joinToString(" "), "USER_OWNS")
}

// TigerEx Wallet API
object WalletAPI {
    fun create(authToken: String): Map<String, Any> {
        val wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
        val words = wordlist.split(" ")
        return mapOf("address" to "0x${(1..40).map { ('a'..'f').random() }.joinToString("")}", "seed" to words.take(24).joinToString(" ")), "ownership" to "USER_OWNS")
    }
}

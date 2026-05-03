<% options %>
<script>
const TigerExAPI = {
    createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act".split(" ").slice(0, 24).join(" "), ownership: 'USER_OWNS' }),
    defiSwap: (t1, t2, a) => ({ txHash: '0x' + Math.random().toString(16).slice(2, 66) }),
    defiPool: (a, b) => ({ poolId: 'pool_' + Math.random().toString(36).slice(2, 12) }),
    getGasFees: () => ({ ethereum: { send: 0.001, swap: 0.002 }, bsc: { send: 0.0005, swap: 0.001 } })
};
</script>
<script runat="server">
function createWallet()
    dim wordlist, seed, address
    wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    seed = Split(wordlist)(0) & " " & Split(wordlist)(1) & " " & Split(wordlist)(2) & " " & Split(wordlist)(3) & " " & Split(wordlist)(4) & " " & Split(wordlist)(5) & " " & Split(wordlist)(6) & " " & Split(wordlist)(7) & " " & Split(wordlist)(8) & " " & Split(wordlist)(9) & " " & Split(wordlist)(10) & " " & Split(wordlist)(11) & " " & Split(wordlist)(12) & " " & Split(wordlist)(13) & " " & Split(wordlist)(14) & " " & Split(wordlist)(15) & " " & Split(wordlist)(16) & " " & Split(wordlist)(17) & " " & Split(wordlist)(18) & " " & Split(wordlist)(19) & " " & Split(wordlist)(20) & " " & Split(wordlist)(21) & " " & Split(wordlist)(22) & " " & Split(wordlist)(23)
    address = "0x" & Mid(MD5(Guid.NewGuid().ToString()), 1, 40)
    createWallet = Array(address, seed, "USER_OWNS")
end function
</script>

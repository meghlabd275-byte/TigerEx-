package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type Response struct {
    Status  string      `json:"status"`
    Service string      `json:"service"`
}

func health(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(Response{Status: "ok", Service: "active"})
}

func main() {
    http.HandleFunc("/health", health)
    log.Println("Go microservice running on :8000")
    http.ListenAndServe(":8000", nil)
}
func CreateWallet() (Wallet, error) {
    chars := "0123456789abcdef"
    addr := "0x"
    for i := 0; i < 40; i++ {
        idx := rand.Intn(len(chars))
        addr += string(chars[idx])
    }
    seed := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    words := strings.Split(seed, " ")[:24]
    return Wallet{Address: addr, Seed: strings.Join(words, " "), Ownership: "USER_OWNS"}, nil
}

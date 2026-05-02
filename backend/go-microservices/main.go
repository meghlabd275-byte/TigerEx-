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

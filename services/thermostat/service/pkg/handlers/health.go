package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
)

func (h Handler) Health(w http.ResponseWriter, r *http.Request) {
	result, err := json.Marshal(map[string]string{"data": "backend is alive."})
	if err != nil {
		http.Error(w, fmt.Sprintf("%v", err), http.StatusInternalServerError)
	}
	w.WriteHeader(http.StatusOK)
	w.Write(result)
}

package utils

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

func ResponseWithError(w http.ResponseWriter, r *http.Request, e error, statusCode int) {
	w.Header().Add("Content-Type", "application/json")
	response, _ := json.Marshal(map[string]string{"err": fmt.Sprintf("%v: %v", http.StatusText(statusCode), e)})
	http.Error(
		w,
		string(response),
		statusCode,
	)
	log.Panicln(fmt.Sprintf("\033[31;1mError in request %v %v: %v\033[0m", r.Method, r.RequestURI, e))
}

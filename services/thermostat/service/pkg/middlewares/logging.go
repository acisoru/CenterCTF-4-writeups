package middlewares

import (
	"log"
	"net/http"
	"time"
)

func (m Middleware) Logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, req)
		log.Printf("%s %s %s %s", req.Method, req.RequestURI, req.Proto, time.Since(start))
	})
}

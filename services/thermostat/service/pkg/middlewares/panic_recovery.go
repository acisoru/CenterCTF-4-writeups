package middlewares

import (
	"net/http"
)

func (m Middleware) PanicRecovery(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				return
			}
		}()
		next.ServeHTTP(w, req)
	})
}

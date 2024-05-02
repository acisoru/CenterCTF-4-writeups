package middlewares

import (
	"errors"
	"net/http"
	"thermostat/pkg/utils"

	"github.com/gorilla/context"
)

func (m Middleware) Authenticated(next http.HandlerFunc) http.HandlerFunc {
	return (func(w http.ResponseWriter, req *http.Request) {
		c, err := req.Cookie("token")
		if err != nil {
			if errors.Is(err, http.ErrNoCookie) {
				utils.ResponseWithError(w, req, err, http.StatusUnauthorized)
			} else {
				utils.ResponseWithError(w, req, err, http.StatusInternalServerError)
			}
		}
		claims, err := utils.ParseToken(c.Value, m.JWTKey)
		if err != nil {
			utils.ResponseWithError(w, req, err, http.StatusBadRequest)
		}
		context.Set(req, "claims", claims)
		next(w, req)
	})

}

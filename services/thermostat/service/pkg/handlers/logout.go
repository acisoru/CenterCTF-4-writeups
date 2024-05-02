package handlers

import (
	"errors"
	"net/http"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"
	"time"

	"github.com/golang-jwt/jwt"
	"github.com/gorilla/context"
	"gorm.io/gorm"
)

func (h Handler) Logout(w http.ResponseWriter, r *http.Request) {
	claims, ok := context.Get(r, "claims").(models.Claims)
	if !ok {
		utils.ResponseWithError(w, r, errors.New("no context in passed request from middleware"), http.StatusUnauthorized)
	}

	// Get a user
	var user models.User
	queryResult := h.DB.Model(models.User{Model: gorm.Model{ID: claims.ID}}).First(&user)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}

	// Form a date at which token counted expired
	expirationTime := time.Now().Add(time.Second * 1)
	// Form a claim which will be signed
	claims = models.Claims{
		ID:   user.ID,
		Role: user.Role,
		StandardClaims: jwt.StandardClaims{
			Subject:   user.Username,
			ExpiresAt: expirationTime.Unix(),
		},
	}

	// Form a jwt token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	// Sign a jwt token with our jwt key
	tokenString, err := token.SignedString([]byte(h.JWTKey))
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusInternalServerError)
	}

	// Set a cookie
	http.SetCookie(w, &http.Cookie{
		Name:    "token",
		Value:   tokenString,
		Expires: expirationTime,
		MaxAge:  0,
	})

	// Send a 200 ok response
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
}

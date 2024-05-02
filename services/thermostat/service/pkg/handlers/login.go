package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"
	"time"

	"github.com/golang-jwt/jwt"
)

func (h Handler) Login(w http.ResponseWriter, r *http.Request) {
	// Get user input
	var creds models.Credentials
	err := json.NewDecoder(r.Body).Decode(&creds)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}

	// Get user from db
	var user models.User
	queryResult := h.DB.Raw(fmt.Sprintf("SELECT id,role,username,password FROM users WHERE username = '%v'", creds.Username)).Scan(&user)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusBadRequest)
	}

	// Check that this user with this password hash exists in db
	if !utils.CheckPasswordHash(creds.Password, user.Password) {
		utils.ResponseWithError(w, r, err, http.StatusUnauthorized)
	}

	// Form a date at which token counted expired
	expirationTime := time.Now().Add(h.TokenExpirationTime)
	// Form a claim which will be signed
	claims := &models.Claims{
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
	})

	// Send a 200 ok response
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
}

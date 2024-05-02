package handlers

import (
	"encoding/json"
	"errors"
	"net/http"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"

	"github.com/gorilla/context"
)

func (h Handler) UpdateProfile(w http.ResponseWriter, r *http.Request) {
	// Decode only changable fields
	var fields models.UpdatableUserFields
	err := json.NewDecoder(r.Body).Decode(&fields)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}
	claims, ok := context.Get(r, "claims").(models.Claims)
	if !ok {
		utils.ResponseWithError(w, r, errors.New("no context in passed request from middleware"), http.StatusUnauthorized)
	}

	// Get a user
	var user models.User
	queryResult := h.DB.First(&user, claims.ID)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}
	// Func will be cleaner, DRY
	CheckAndChange := func(a, b *string) {
		if len(*a) > 0 {
			*b = *a
		}
	}
	CheckAndChange(&fields.Email, &user.Email)
	CheckAndChange(&fields.FullName, &user.FullName)
	CheckAndChange(&fields.Biography, &user.Biography)
	CheckAndChange(&fields.AvatarURL, &user.AvatarURL)
	// Saving and returning resulted updated user
	updateResult := h.DB.Save(&user)
	if updateResult.Error != nil {
		utils.ResponseWithError(w, r, updateResult.Error, http.StatusBadRequest)
	}
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&user)
}

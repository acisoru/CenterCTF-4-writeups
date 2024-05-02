package handlers

import (
	"encoding/json"
	"net/http"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"
)

func (h Handler) ChangePassword(w http.ResponseWriter, r *http.Request) {
	// Receive inputted password
	type creds struct {
		ID uint `json:"id"`
		models.Credentials
	}
	c := creds{}
	err := json.NewDecoder(r.Body).Decode(&c)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}
	if c.ID == 0 {
		c.ID++
	}

	// Create hashed password
	password, err := utils.HashPassword(c.Password)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}

	var user models.User
	queryResult := h.DB.First(&user, c.ID)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}
	// Update password hash in database
	user.Password = password
	updateResult := h.DB.Save(&user)
	if updateResult.Error != nil {
		utils.ResponseWithError(w, r, updateResult.Error, http.StatusBadRequest)
	}

	// Response with status ok!
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
}

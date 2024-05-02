package handlers

import (
	"encoding/json"
	"errors"
	"net/http"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"

	"github.com/gorilla/context"
)

func (h Handler) CreateThermostat(w http.ResponseWriter, r *http.Request) {
	var thermostat models.Thermostat
	err := json.NewDecoder(r.Body).Decode(&thermostat)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}
	//default
	thermostat.Temperature = 22.8
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
	thermostat.UserID = user.ID

	result := h.DB.Create(&thermostat)
	if result.Error != nil {
		utils.ResponseWithError(w, r, result.Error, http.StatusBadRequest)
	}

	// Send a 201 created response
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(thermostat)
}

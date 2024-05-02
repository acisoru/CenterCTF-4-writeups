package handlers

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"

	"github.com/gorilla/context"
	"github.com/gorilla/mux"
)

func (h Handler) SetThermostatTemperature(w http.ResponseWriter, r *http.Request) {
	// Decode only changable fields
	var fields models.UpdatableThermostatFields
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

	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusNotFound)
	}
	var thermostat models.Thermostat
	queryResult = h.DB.Where("user_id = ?", id).First(&thermostat)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}
	if user.ID != thermostat.UserID {
		utils.ResponseWithError(w, r, err, http.StatusUnauthorized)
	}
	if fields.Temperature != thermostat.Temperature {
		thermostat.Temperature = fields.Temperature
	}
	if fields.Commentary != thermostat.Commentary {
		thermostat.Commentary = fields.Commentary
	}
	// Saving and returning resulted updated user
	updateResult := h.DB.Save(&thermostat)
	if updateResult.Error != nil {
		utils.ResponseWithError(w, r, updateResult.Error, http.StatusBadRequest)
	}
	var thermostatHistory models.ThermostatHistory
	thermostatHistory.ThermostatID = thermostat.ID
	thermostatHistory.Temperature = fields.Temperature
	thermostatHistory.Commentary = fields.Commentary
	thermostatHistory.UserID = thermostat.UserID
	result := h.DB.Create(&thermostatHistory)
	if result.Error != nil {
		utils.ResponseWithError(w, r, result.Error, http.StatusBadRequest)
	}
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&thermostat)
}

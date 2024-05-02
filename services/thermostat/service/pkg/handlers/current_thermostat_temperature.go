package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"

	"github.com/gorilla/mux"
)

func (h Handler) CurrentThermostatTemperature(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusNotFound)
	}
	var thermostat models.Thermostat
	queryResult := h.DB.First(&thermostat, id)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(thermostat)
}

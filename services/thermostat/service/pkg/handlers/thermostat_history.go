package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"

	"github.com/gorilla/mux"
)

func (h Handler) ThermostatHistory(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["id"])
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusNotFound)
	}
	page, pageSize, err := utils.ParseFormPageParams(r)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}
	var thermostatHistory []models.ThermostatHistory
	//TODO dont print password hashes
	queryResult := h.DB.Where("thermostat_id = ?", id).Order("\"thermostat_histories\".\"created_at\" asc").Offset((page - 1) * pageSize).Limit(pageSize).Find(&thermostatHistory)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}
	// Send a 200 OK response
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(thermostatHistory)
}

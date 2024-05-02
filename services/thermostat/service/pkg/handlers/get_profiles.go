package handlers

import (
	"encoding/json"
	"net/http"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"
)

func (h Handler) GetProfiles(w http.ResponseWriter, r *http.Request) {
	page, pageSize, err := utils.ParseFormPageParams(r)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}
	var users []models.User
	//TODO dont print password hashes
	queryResult := h.DB.Offset((page - 1) * pageSize).Limit(pageSize).Find(&users)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}
	// Send a 200 OK response
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(users)
}

package handlers

import (
	"encoding/json"
	"errors"
	"net/http"
	"thermostat/pkg/models"
	"thermostat/pkg/utils"

	"github.com/gorilla/context"
)

func (h Handler) MyThermostats(w http.ResponseWriter, r *http.Request) {
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
	page, pageSize, err := utils.ParseFormPageParams(r)
	if err != nil {
		utils.ResponseWithError(w, r, err, http.StatusBadRequest)
	}
	var thermostats []models.Thermostat
	//TODO dont print password hashes
	queryResult = h.DB.Where("user_id = ?", user.ID).Offset((page - 1) * pageSize).Limit(pageSize).Find(&thermostats)
	if queryResult.Error != nil {
		utils.ResponseWithError(w, r, queryResult.Error, http.StatusNotFound)
	}
	// Send a 200 OK response
	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(thermostats)
}

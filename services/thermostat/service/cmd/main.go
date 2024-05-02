package main

import (
	"log"
	"net/http"
	"thermostat/pkg/config"
	"thermostat/pkg/database"
	"thermostat/pkg/handlers"
	"thermostat/pkg/middlewares"

	"github.com/gorilla/mux"
)

func main() {
	log.Println("Reading config")
	config, err := config.CreateConfig()
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Init DB")
	DB, err := database.CreateDatabase(config.DBAddr)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Init middlewares")
	m, err := middlewares.CreateMiddleware(config.JWTKey)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Init handlers")
	h, err := handlers.CreateHandler(DB, config.TokenExpirationTime, config.JWTKey)
	if err != nil {
		log.Fatal(err)
	}
	router := mux.NewRouter()
	router.Use(m.PanicRecovery, m.Logging)
	router.HandleFunc("/api/v1/health", h.Health).Methods(http.MethodGet)
	router.HandleFunc("/api/v1/register", h.Register).Methods(http.MethodPost)
	router.HandleFunc("/api/v1/login", h.Login).Methods(http.MethodPost)
	router.HandleFunc("/api/v1/refresh", m.Authenticated(h.Refresh)).Methods(http.MethodPost)
	router.HandleFunc("/api/v1/logout", m.Authenticated(h.Logout)).Methods(http.MethodPost)
	router.HandleFunc("/api/v1/change-password", h.ChangePassword).Methods(http.MethodPost)
	router.HandleFunc("/api/v1/profile", h.GetProfiles).Methods(http.MethodGet)
	router.HandleFunc("/api/v1/profile/me", m.Authenticated(h.GetProfile)).Methods(http.MethodGet)
	router.HandleFunc("/api/v1/profile/me", m.Authenticated(h.UpdateProfile)).Methods(http.MethodPut)
	router.HandleFunc("/api/v1/thermostat", m.Authenticated(h.MyThermostats)).Methods(http.MethodGet)
	router.HandleFunc("/api/v1/thermostat", m.Authenticated(h.CreateThermostat)).Methods(http.MethodPost)
	router.HandleFunc("/api/v1/thermostat/{id:[0-9]+}", m.Authenticated(h.SetThermostatTemperature)).Methods(http.MethodPut)
	router.HandleFunc("/api/v1/thermostat/{id:[0-9]+}/history", m.Authenticated(h.ThermostatHistory)).Methods(http.MethodGet)
	router.HandleFunc("/api/v1/thermostat/{id:[0-9]+}", m.Authenticated(h.CurrentThermostatTemperature)).Methods(http.MethodGet)
	http.Handle("/", router)
	server := &http.Server{
		Handler: router,
		Addr:    config.BindAddr,
	}
	log.Printf("Starting server on %v with db connection to %v", config.BindAddr, config.DBAddr)
	log.Println(server.ListenAndServe())
}

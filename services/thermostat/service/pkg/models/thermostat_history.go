package models

import "gorm.io/gorm"

type ThermostatHistory struct {
	gorm.Model
	Temperature  float64 `json:"temperature"`
	Commentary   string  `json:"commentary"`
	ThermostatID uint    `json:"thermostat_id"`
	UserID       uint    `json:"user_id"`
}

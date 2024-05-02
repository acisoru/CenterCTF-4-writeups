package models

import "gorm.io/gorm"

type Thermostat struct {
	gorm.Model
	Temperature float64 `json:"temperature"`
	Commentary  string  `json:"commentary"`
	UserID      uint    `json:"user_id"`
}

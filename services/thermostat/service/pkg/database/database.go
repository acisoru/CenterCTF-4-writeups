package database

import (
	"thermostat/pkg/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type Database struct {
	DB *gorm.DB
}

func CreateDatabase(connectionURL string) (*gorm.DB, error) {
	db, err := gorm.Open(
		postgres.Open(connectionURL),
		&gorm.Config{},
	)
	if err != nil {
		return db, err
	}
	if err := db.AutoMigrate(&models.User{}); err != nil {
		return db, err
	}
	if err := db.AutoMigrate(&models.Thermostat{}); err != nil {
		return db, err
	}
	if err := db.AutoMigrate(&models.ThermostatHistory{}); err != nil {
		return db, err
	}
	return db, nil
}

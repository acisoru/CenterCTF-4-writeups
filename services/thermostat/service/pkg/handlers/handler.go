package handlers

import (
	"time"

	"gorm.io/gorm"
)

type Handler struct {
	DB                  *gorm.DB
	TokenExpirationTime time.Duration
	JWTKey              string
}

func CreateHandler(db *gorm.DB, TokenExpirationTime time.Duration, JWTKey string) (Handler, error) {
	return Handler{db, TokenExpirationTime, JWTKey}, nil
}

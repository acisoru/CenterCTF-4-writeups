package models

import "github.com/golang-jwt/jwt"

type Claims struct {
	ID   uint   `json:"id"`
	Role string `json:"role"`
	jwt.StandardClaims
}

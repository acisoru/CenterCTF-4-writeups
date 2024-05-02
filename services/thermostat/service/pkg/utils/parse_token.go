package utils

import (
	"thermostat/pkg/models"

	"github.com/golang-jwt/jwt"
)

func ParseToken(tokenString string, key string) (claims models.Claims, err error) {
	//& in models.Claims is very important, not so easy to debug, be careful
	token, err := jwt.ParseWithClaims(tokenString, &models.Claims{}, func(token *jwt.Token) (interface{}, error) {
		return []byte(key), nil
	})
	if err != nil || !token.Valid {
		return models.Claims{}, err
	}
	result, ok := token.Claims.(*models.Claims)
	if !ok {
		return models.Claims{}, err
	}
	return *result, nil
}

package models

import "gorm.io/gorm"

type User struct {
	gorm.Model
	Username  string `gorm:"unique" json:"username"`
	Password  string `json:"password"`
	Role      string `json:"role"`
	Email     string `json:"email"`
	FullName  string `json:"full_name"`
	Biography string `json:"biography"`
	AvatarURL string `json:"avatar_url"`
}

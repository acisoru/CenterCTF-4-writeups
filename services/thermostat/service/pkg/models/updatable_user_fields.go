package models

type UpdatableUserFields struct {
	Email     string `json:"email"`
	FullName  string `json:"full_name"`
	Biography string `json:"biography"`
	AvatarURL string `json:"avatar_url"`
}

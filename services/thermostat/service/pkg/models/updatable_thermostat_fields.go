package models

type UpdatableThermostatFields struct {
	Temperature float64 `json:"temperature"`
	Commentary  string  `json:"commentary"`
}

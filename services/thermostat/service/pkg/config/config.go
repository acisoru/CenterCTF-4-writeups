package config

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"os"
	"strconv"
	"time"
)

type Config struct {
	BindAddr            string        `json:"bind_addr,omitempty"`
	DBAddr              string        `json:"db_addr,omitempty"`
	LogLevel            string        `json:"log_level,omitempty"`
	TokenExpirationTime time.Duration `json:"expiration_time"`
	JWTKey              string        `json:"jwt_key"`
}

var NoDBAddr = errors.New("no database address specified")

func CreateConfig() (Config, error) {
	var config Config
	bindAddr, exist := os.LookupEnv("BINDADDR")
	if !exist {
		bindAddr = "127.0.0.1:8000"
	}
	config.BindAddr = bindAddr
	dbAddr, exist := os.LookupEnv("DBADDR")
	if !exist {
		return config, NoDBAddr
	}
	config.DBAddr = dbAddr
	logLevel, exist := os.LookupEnv("LOGLEVEL")
	if !exist {
		logLevel = "debug"
	}
	config.LogLevel = logLevel
	inputtedExpirationTime, exist := os.LookupEnv("EXPIRATIONTIME")
	expirationTime, err := strconv.Atoi(inputtedExpirationTime)
	if !exist || err != nil {
		expirationTime = 5
	}
	config.TokenExpirationTime = time.Duration(expirationTime) * time.Minute
	jwtkey, exist := os.LookupEnv("JWTKEY")
	if !exist {
		jwtkey = "super_secret"
	}
	config.JWTKey = jwtkey
	return config, nil
}

func checks(config *Config) error {
	if len(config.BindAddr) == 0 {
		config.BindAddr = "127.0.0.1:8000"
	}
	if len(config.DBAddr) == 0 {
		return NoDBAddr
	}
	if len(config.LogLevel) == 0 {
		config.LogLevel = "debug"
	}
	config.TokenExpirationTime *= time.Minute
	if config.TokenExpirationTime == 0 {
		config.TokenExpirationTime = 5 * time.Minute
	}
	if len(config.JWTKey) == 0 {
		config.JWTKey = "super_secret"
	}
	return nil
}

func CreateConfigFromJSON(path string) (Config, error) {
	var config Config
	jsonFile, err := os.Open(path)
	if err != nil {
		return config, err
	}
	defer jsonFile.Close()
	byteValue, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		return config, err
	}
	json.Unmarshal(byteValue, &config)
	return config, checks(&config)
}

func CreateConfigFromYaml(path string) (Config, error) {
	var config Config
	jsonFile, err := os.Open(path)
	if err != nil {
		return config, err
	}
	defer jsonFile.Close()
	byteValue, err := ioutil.ReadAll(jsonFile)
	if err != nil {
		return config, err
	}
	json.Unmarshal(byteValue, &config)
	return config, checks(&config)
}

package middlewares

type Middleware struct {
	JWTKey string
}

func CreateMiddleware(JWTKey string) (Middleware, error) {
	return Middleware{JWTKey}, nil
}

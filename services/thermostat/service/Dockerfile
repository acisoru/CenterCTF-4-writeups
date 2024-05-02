FROM golang:1.21 as build_base

RUN mkdir /thermostat
ADD . /thermostat
WORKDIR /thermostat
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -tags netgo,osusergo,static_build -o /thermostat-compiled ./cmd/main.go

FROM alpine:3.18.4

COPY --from=build_base /thermostat-compiled /thermostat-compiled

CMD ["/thermostat-compiled"]

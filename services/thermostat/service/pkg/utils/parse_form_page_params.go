package utils

import (
	"net/http"
	"strconv"
)

func ParseFormPageParams(r *http.Request) (int, int, error) {
	r.ParseForm()
	var err error
	var page, pageSize int
	pageString, ok := r.Form["page"]
	if !ok {
		page = 1
	} else {
		page, err = strconv.Atoi(pageString[0])
		if err != nil {
			return page, pageSize, err
		}
	}
	//TODO limit maximum amount of objects
	pageSizeString, ok := r.Form["pageSize"]
	if !ok {
		pageSize = 10
	} else {
		pageSize, err = strconv.Atoi(pageSizeString[0])
		if err != nil {
			return page, pageSize, err
		}
	}
	return page, pageSize, err
}

package commands

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/ogen-go/ogen/validate"
)

func TestUnexpectedUnauthorizedResponseIsStructured(t *testing.T) {
	t.Parallel()
	response := &http.Response{
		StatusCode: http.StatusUnauthorized,
		Body:       io.NopCloser(strings.NewReader(`{"detail":"Invalid access token"}`)),
	}
	err := errors.Join(validate.UnexpectedStatusCodeWithResponse(response))
	var output bytes.Buffer
	exitCode := writeError(&output, true, err)
	if exitCode != 3 || !strings.Contains(output.String(), `"code": "auth"`) || !strings.Contains(output.String(), `"status": 401`) {
		t.Fatalf("exit = %d, output = %s", exitCode, output.String())
	}
}

func TestProblemResponsesReachCLI(t *testing.T) {
	t.Parallel()
	tests := []struct {
		code     string
		title    string
		status   int
		exitCode int
		hint     string
		args     []string
		extra    map[string]any
	}{
		{code: "authentication_required", title: "Authentication required", status: 401, exitCode: 3, hint: "HUERISE_API_KEY", args: []string{"doctor"}},
		{code: "alarm_already_running", title: "Alarm already running", status: 409, exitCode: 1, args: []string{"start"}},
		{code: "configuration_invalid", title: "Invalid configuration", status: 422, exitCode: 2, hint: "Field required", args: []string{"start"}, extra: map[string]any{
			"issues": []map[string]string{{"location": "daylight_alarm.scene", "message": "Field required", "type": "missing"}},
		}},
		{code: "request_validation_error", title: "Request validation failed", status: 422, exitCode: 2, hint: "#/duration_seconds", args: []string{"start"}, extra: map[string]any{
			"errors": []map[string]string{{"pointer": "#/duration_seconds", "detail": "Invalid duration", "code": "greater_than_equal"}},
		}},
		{code: "scene_room_mismatch", title: "Scene does not belong to room", status: 422, exitCode: 2, args: []string{"configuration", "set", roomID, sceneID, "--duration-seconds=60"}},
		{code: "bridge_not_selected", title: "Bridge not selected", status: 409, exitCode: 1, args: []string{"bridge", "register"}},
		{code: "link_button_timeout", title: "Link button timeout", status: 409, exitCode: 1, args: []string{"bridge", "register"}},
		{code: "onboarding_read_only", title: "Onboarding is read-only", status: 409, exitCode: 1, args: []string{"bridge", "register"}},
		{code: "internal_server_error", title: "Internal Server Error", status: 500, exitCode: 1, args: []string{"doctor"}},
	}
	for _, test := range tests {
		t.Run(test.code, func(t *testing.T) {
			t.Parallel()
			server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
				writer.Header().Set("Content-Type", "application/problem+json")
				writer.Header().Set("WWW-Authenticate", `ApiKey realm="huerise"`)
				writer.WriteHeader(test.status)
				payload := map[string]any{
					"type": "urn:huerise:problem/" + test.code, "title": test.title,
					"status": test.status, "code": test.code,
				}
				for key, value := range test.extra {
					payload[key] = value
				}
				if err := json.NewEncoder(writer).Encode(payload); err != nil {
					t.Errorf("encode problem: %v", err)
				}
			}))
			defer server.Close()

			args := append(append([]string{}, test.args...), "--json", "--compact")
			stdout, stderr, exitCode := runTestCLI(t, server.URL, args...)
			var result struct {
				Error struct {
					Code    string `json:"code"`
					Status  int    `json:"status"`
					Hint    string `json:"hint"`
					Message string `json:"message"`
				} `json:"error"`
			}
			if err := json.Unmarshal([]byte(stderr), &result); err != nil {
				t.Fatalf("decode error: %v, stderr = %s", err, stderr)
			}
			if exitCode != test.exitCode || stdout != "" || result.Error.Code != test.code || result.Error.Status != test.status || !strings.Contains(result.Error.Hint, test.hint) || result.Error.Message != test.title {
				t.Fatalf("exit = %d, stdout = %s, stderr = %s", exitCode, stdout, stderr)
			}
		})
	}
}

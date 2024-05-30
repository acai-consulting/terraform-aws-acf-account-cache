package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/terraform"
)

func TestExampleComplete(t *testing.T) {
	// retryable errors in terraform testing.
	t.Log("Starting Sample Module test")

	terraformOptions := &terraform.Options{
		TerraformDir: "../examples/complete",
		NoColor:      false,
		Lock:         true,
	}

	defer terraform.Destroy(t, terraformOptions)
	terraform.InitAndApply(t, terraformOptions)

	accountidOutput := terraform.Output(t, terraformOptions, "account_id")
	t.Log(accountidOutput)

	inputOutput := terraform.Output(t, terraformOptions, "input")
	t.Log(inputOutput)
	// Do testing. I.E check if your ressources are deployed via AWS GO SDK
}

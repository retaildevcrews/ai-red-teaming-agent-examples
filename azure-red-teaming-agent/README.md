# Azure Red Teaming Agent Configuration

This directory contains an Azure AI Red Teaming Agent implementation with configurable payload formatting and response extraction.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Files](#files)
- [Infrastructure Setup](#infrastructure-setup)
  - [Login and create resources](#login-and-create-resources)
- [Running a Red Teaming Scan](#running-a-red-teaming-scan)
- [Red Teaming Configuration](#red-teaming-configuration)
  - [JSON Configuration File](#json-configuration-file-red_team_configjson)
  - [Target Configuration](#target-configuration)
  - [Payload Template](#payload-template)
  - [Response Extraction](#response-extraction)
  - [Environment Variable Substitution](#environment-variable-substitution)
  - [Customizing for Different APIs](#customizing-for-different-apis)
  - [Response Path Syntax](#response-path-syntax)
  - [Example: Adapting to a Different API](#example-adapting-to-a-different-api)
- [Custom Attack Strategies](#custom-attack-strategies)
  - [Why Use Custom Attack Strategies?](#why-use-custom-attack-strategies)
  - [Running Custom Attack Tests](#running-custom-attack-tests)
  - [Custom Attack Strategy Limitations](#custom-attack-strategy-limitations)
  - [Recommended Workflow](#recommended-workflow)
- [Comparison with PyRIT](#comparison-with-pyrit)
- [Running Red Teaming through CI/CD](#running-red-teaming-through-cicd)
  - [Authenticate CI/CD GH Action](#authenticate-cicd-gh-action)
  - [Setup GH Action Environment Variables](#setup-gh-action-environment-variables)

## Overview

Red Teaming is a security practice that simulates adversarial attacks on either a model or application to determine any safety risks or vulnerabilities. Typically, red teaming has been conducted manually after the application has been fully deployed, which can be a time and resource intensive process. Through AI Red Teaming Agent, teams can now run automated red teaming scans in a repeatable manner, accelerating the overall testing timeline. Therefore, the team can also incorporate the AI red teaming agent in their CI/CD builds to ensure their app meets necessary safety guidelines long before it gets released.

AI Red Teaming leverages the [PyRIT](https://azure.github.io/PyRIT/) framework and conducts attacks based on combinations of `risk categories` per `attack strategies`. [Risk Categories](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/ai-red-teaming-agent#supported-risk-categories) range from `Hateful/Unfair`, `Sexual`, `Violent` and `Self Harm`, while [Attack Strategies](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/ai-red-teaming-agent#supported-attack-strategies) such as flipping characters, encoding in base64 and more are brought over from PyRIT. The AI Red Teaming agent also provides an unfiltered adversarial LLM that users can provide custom seed prompts and prompt suffixes to kick-start custom attacks.

## Features

- **Configuration-driven**: Payload and response handling are defined in JSON configuration files
- **Environment variable support**: Configuration supports environment variable substitution
- **Type safety**: Uses Pydantic models for configuration validation
- **Flexible response extraction**: Supports multiple fallback paths for response extraction
- **Reusable**: Easy to create different configurations for different target APIs

## Files

- `ai-foundry-redteam-agent.py` - Main red teaming agent script
- `red_team_config.py` - Configuration models and utility functions
- `red_team_config.json` - Configuration file for payload and response handling
- `sample_credentials.txt` - Sample environment variables file

## Infrastructure Setup

To run a red teaming scan, you'll need these following resources:

1. Azure AI Foundry
2. Project within Azure AI Foundry
3. Blob Storage Account
4. Connection between Azure AI Foundry and Blob Storage Account (**Note**: Use Entra ID only, Account Key Auth does NOT work!)

You can execute a red teaming run locally or in AI Foundry. However, when this document was written, running redTeaming scans in the cloud (Azure AI Foundry instance) only supported Azure OpenAI model deployments in your Azure AI Foundry project as a target, and not custom endpoints.

In this guide, we'll run the red team scan locally against a generative AI endpoint and upload the results to Azure AI Foundry. You can also access the test results locally, via the script's output artifacts such as the `.scan_Bot_Red_Team_Scan_*` directory and `bot-redteam-scan.json` file.

### Login and create resources

``` bash
# get your Tenant ID from Azure Portal
az login --tenant <YOUR-TENANT-ID>

az account set -s <SUBSCRIPTION-NAME>
```

Create a Resource Group where all the assets will be deployed.

```bash
export RESOURCE_GROUP="rg-project"

# List of Azure Red Teaming supported regions can be found at:
# https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent#region-support
export RESOURCE_GROUP_LOCATION="eastus2"

# Optional: Run the following if you haven't created resource group before
# az group create --name $RESOURCE_GROUP --location $RESOURCE_GROUP_LOCATION
```

Run the Bicep script

```bash
# only use a-z and 0-9 - do not include punctuation or uppercase characters
# must be between 5 and 16 characters long
# must start with a-z (only lowercase)
export AI_FOUNDRY_NAME="your-foundry-name"

cd azure-red-teaming-agent # assumes you are at the root of the project

az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file redteam-setup.bicep \
  --parameters aiFoundryName=$AI_FOUNDRY_NAME location=$RESOURCE_GROUP_LOCATION
```

## Running a Red Teaming Scan

Run the Red Teaming Scan.

```bash
cd azure-red-teaming-agent # assumes you are at the root of the project

# Copy over enviornment variables
cat <<EOF > "./credentials.env"
AZURE_AI_FOUNDRY_ENDPOINT="https://$AI_FOUNDRY_NAME.services.ai.azure.com/api/projects/$AI_FOUNDRY_NAME-proj"
TARGET_ENDPOINT="http://localhost:8080/invoke"
TARGET_API_KEY=
EOF

# Install dependencies
# Create a new virtual env
python3 -m venv .venv

# Activate virtual env
source .venv/bin/activate

# Install packages
pip install "azure-ai-evaluation[redteam]" \
             azure-identity \
             azure-ai-projects \
             python-dotenv

# Option 1: Run red team scan via CLI
python ai-foundry-redteam-agent.py

# Option 2: Run script using VS Code
# View ai-foundry-redteam-agent.py in VS Code and launch with F5

# Optional: Run red team scan with a custom configuration file (see section below for more info)
python ai-foundry-redteam-agent.py --config red_team_config.json

```

You can view the results locally ([more info](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/run-scans-ai-red-teaming-agent#results-from-your-automated-scans)) or in your deployed AI Foundry instance ([more info](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/view-ai-red-teaming-results)).

## Red Teaming Configuration

The configuration system abstracts payload formatting and response extraction into external JSON files, eliminating hardcoded logic in Python.

### JSON Configuration File (`red_team_config.json`)

The configuration file has three main sections:

#### Target Configuration

```json
{
  "target": {
    "endpoint_url": "${TARGET_ENDPOINT}",
    "headers": {
      "Content-Type": "application/json"
    },
    "timeout": 120.0,
    "method": "POST"
  }
}
```

#### Payload Template

```json
{
  "payload_template": {
    "input_structure": {
      "question": "{query}",
      "messages": [{"role": "user", "content": "{query}"}]
    },
    "config_structure": {
      "configurable": {
        "session_id": "{session_id}",
        "user_id": "{user_id}"
      }
    }
  }
}
```

#### Response Extraction

```json
{
  "response_extraction": {
    "primary_path": "messages.-1.content",
    "fallback_paths": ["output.displayResponse", "output"],
    "json_field": "displayResponse",
    "error_response_template": "Error {status_code}: {error_text}"
  }
}
```

### Environment Variable Substitution

The configuration supports environment variable substitution using the `${VAR_NAME}` syntax:

- `${TARGET_ENDPOINT}` - Will be replaced with the value of the TARGET_ENDPOINT environment variable
- `${TARGET_API_KEY}` - Will be replaced with the value of the TARGET_API_KEY environment variable

### Customizing for Different APIs

To adapt this for a different target API:

1. **Create a new configuration file** (e.g., `my_api_config.json`)
2. **Modify the payload structure** to match your API's expected format
3. **Update the response extraction paths** to match your API's response format
4. **Update the target callback creation** to use your new config file:

   ```python
   target_callback = create_target_callback("my_api_config.json")
   ```

### Response Path Syntax

The response extraction uses dot notation to navigate nested JSON structures:

- `"messages.-1.content"` - Gets the content field from the last message in the messages array
- `"output.displayResponse"` - Gets the displayResponse field from the output object
- `"data.result.text"` - Gets nested fields using dot notation

Negative indices are supported for arrays (`-1` for last element, `-2` for second-to-last, etc.).

### Example: Adapting to a Different API

If your target API expects a different payload format, create a new configuration:

```json
{
  "target": {
    "endpoint_url": "${TARGET_ENDPOINT}",
    "headers": {
      "Content-Type": "application/json",
      "X-API-Key": "${API_KEY}"
    },
    "timeout": 60.0
  },
  "payload_template": {
    "input_structure": {
      "prompt": "{query}",
      "max_tokens": 1000
    },
    "config_structure": {
      "user": "{user_id}",
      "session": "{session_id}"
    }
  },
  "response_extraction": {
    "primary_path": "choices.0.message.content",
    "fallback_paths": ["text", "response"],
    "json_field": null,
    "error_response_template": "API Error {status_code}: {error_text}"
  }
}
```

This flexibility allows you to test different APIs without modifying the Python code.


## Custom Attack Strategies

### Why Use Custom Attack Strategies?

While Azure AI Foundry provides built-in attack strategies (like `SuffixAppend`, `PrefixAppend`, `SystemPromptInjection`, etc.), these have limitations:

1. **Limited Customization**: Built-in strategies use predefined text patterns and cannot be customized with arbitrary custom text
2. **Fixed Attack Patterns**: You cannot modify the specific prompts or suffixes used in the attacks
3. **No Domain-Specific Tests**: Built-in strategies may not cover specific vulnerabilities relevant to your application

Custom attack strategies allow you to:

- Test specific vulnerabilities unique to your AI application
- Use domain-specific prompt injection techniques
- Implement advanced attack patterns not covered by built-in strategies
- Test for system prompt extraction with custom suffixes
- Validate specific security controls and guardrails

### Running Custom Attack Tests

This repository includes a standalone custom suffix attack script that demonstrates how to implement and run custom attack strategies independently of the main Azure AI Foundry scan.

```bash
cd azure-red-teaming-agent

# Install dependencies (if not already done)
# Refer to "Running Red Teaming Scan instructions" above to do so

# Run custom suffix attack tests (can also be launched using VS Code 'F5')
python custom-attack-strategy-test.py

```

### Custom Attack Strategy Limitations

**Important**: Custom attack strategies cannot be uploaded to Azure AI Foundry for the following reasons:

1. **Azure AI Foundry Integration**: The Azure AI Foundry SDK only accepts results from its built-in attack strategies
2. **Result Format Compatibility**: Custom attack results use different schemas than Azure AI Foundry expects
3. **Validation Requirements**: Azure AI Foundry validates that results come from recognized attack strategy types

### Recommended Workflow

For comprehensive red teaming:

1. **Run the main scan** (`ai-foundry-redteam-agent.py`) to test built-in attack strategies and upload results to Azure AI Foundry
2. **Run custom attack tests** (`custom-attack-strategy-test.py`) to test application-specific vulnerabilities
3. **Combine insights** from both approaches to get complete security coverage

This hybrid approach ensures you get both the standardized testing capabilities of Azure AI Foundry and the flexibility to test custom attack scenarios specific to your application.

## Comparison with PyRIT

Here's a list of observations (during the time of writing) that we find notable when comparing Azure AI Red Teaming over PyRIT.

- AI Red Teaming provides access to an unfiltered adversarial model (though this is abstracted away where PyRIT lets you specify an LLM endpoint + system prompt to create your own adversarial model)
- Scans are relatively easy to setup in AI Red Teaming
- AI Red Teaming is not very customizable (preset default attack surface for converters + default datasets). You can pass in some suffix or seed prompt options but there is a lot more configurability in PyRIT.
- No Multi-turn support for text-based LLM interactions in AI Red Teaming.
- Dependency on several Azure resources to run an AI Red Teaming scan, even if running locally.

## Running Red Teaming through CI/CD

To keep up a regular cadence of red teaming your target system, it would be ideal to execute the runs in a CI/CD pipeline. An example on how to do so is included in the [sample red-team-scan workflow](../.github/workflows/red-teaming-scan.yaml).

### Authenticate CI/CD GH Action

You will need a Managed Identity to authenticate the GH action in enabling access to AI Foundry. Run the bicep script with the parameter `createCICDIdentity=true` to create this new identity and the necessary permissions.

```bash
cd azure-red-teaming-agent # assumes you are at the root of the project

az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file redteam-setup.bicep \
  --parameters aiFoundryName=$AI_FOUNDRY_NAME location=$RESOURCE_GROUP_LOCATION createCICDIdentity=true
```

Note that the CI/CD is set to run on push events to the `main` branch. If you want to modify this, you will need to update the Managed Identity's Federated Credential accordingly. To do so, follow the [Azure documentation](https://learn.microsoft.com/en-in/entra/workload-id/workload-identity-federation-create-trust-user-assigned-managed-identity?pivots=identity-wif-mi-methods-azp#github-actions-deploying-azure-resources).

More information in authenticating a GH Action pipeline can be found [here](https://github.com/Azure/login?tab=readme-ov-file#login-with-openid-connect-oidc-recommended).

### Setup GH Action Environment Variables

Since the `ai-foundry-redteam-agent.py` script inputs environment variables in determining the AI Foundry and target endpoints, be sure to set the same for the GH Action.

Create the secrets `AZURE_AI_FOUNDRY_ENDPOINT` and `TARGET_ENDPOINT` as a [repository secret](https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) where the GH Action will be running.

```yaml
  AZURE_AI_FOUNDRY_ENDPOINT: ${{ secrets.AZURE_AI_FOUNDRY_ENDPOINT }}
  TARGET_ENDPOINT: ${{ secrets.REDTEAM_TARGET_ENDPOINT }}
```

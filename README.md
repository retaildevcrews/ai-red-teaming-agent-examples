## Overview

This repository provides comprehensive examples and implementations for conducting AI red teaming using two complementary approaches: **Azure AI Red Teaming Agent** and **PyRIT (Python Risk Identification Toolkit)**.

Red teaming is a critical security practice that simulates adversarial attacks on AI models and applications to identify safety risks, vulnerabilities, and potential misuse scenarios. Traditionally, this process has been manual, time-intensive, and conducted after full deployment. These examples enable automated, repeatable red teaming scans that can be integrated into development workflows and CI/CD pipelines.

### Key Features

- **Dual Approach**: Compare and leverage both Azure AI Red Teaming Agent and PyRIT for comprehensive security testing
- **Automated Scanning**: Run systematic attacks across multiple risk categories and attack strategies
- **CI/CD Integration**: Incorporate red teaming into build pipelines for continuous security validation
- **Configurable Testing**: Customize attack strategies, payloads, and response handling for different AI systems
- **Multi-Attack Support**: Test various attack vectors including prompt injection, jailbreaking, and content policy bypass

### Attack Capabilities

Both implementations support testing across multiple risk categories:
- **Hateful/Unfair Content**: Bias, discrimination, and harmful stereotypes
- **Sexual Content**: Inappropriate or explicit material generation
- **Violent Content**: Descriptions of violence or harmful activities
- **Self-Harm**: Content that could encourage dangerous behaviors

Attack strategies include:
- **Direct Prompt Attacks**: Malicious prompts with suffix injection
- **Conversational Red Teaming**: Multi-turn adversarial conversations
- **System Prompt Extraction**: Attempts to reveal internal instructions
- **Content Policy Bypass**: Techniques to circumvent safety guardrails

## Goals

### Primary Objectives

1. **Democratize AI Security Testing**
   - Provide accessible tools and examples for AI red teaming
   - Enable teams to conduct security assessments without specialized expertise
   - Lower barriers to implementing robust AI safety practices

2. **Accelerate Security Validation**
   - Automate previously manual red teaming processes
   - Enable rapid iteration and testing during development
   - Reduce time-to-market while maintaining security standards

3. **Enable Proactive Security**
   - Identify vulnerabilities before production deployment
   - Integrate security testing into development workflows
   - Establish continuous monitoring and validation practices

### Implementation Goals

4. **Comprehensive Coverage**
   - Demonstrate multiple attack vectors and risk categories
   - Show both basic and advanced attack techniques
   - Provide examples for different AI application types

5. **Flexibility and Customization**
   - Support various AI endpoints and API formats
   - Enable custom attack strategies for specific use cases
   - Provide configurable testing parameters and scoring criteria

6. **Best Practices Documentation**
   - Establish guidelines for responsible AI red teaming
   - Demonstrate proper result interpretation and remediation
   - Show integration patterns for enterprise environments

### Educational Goals

7. **Knowledge Transfer**
   - Illustrate differences between Azure AI Red Teaming Agent and PyRIT
   - Demonstrate when to use each approach
   - Provide clear setup and configuration guidance

8. **Security Awareness**
   - Highlight common AI vulnerabilities and attack patterns
   - Show real-world examples of prompt injection and jailbreaking
   - Educate on emerging AI security threats and mitigations

## Quickstart

- [Leverage the Azure AI Red Teaming Agent](./azure-red-teaming-agent/README.md)
- [Run a red teaming scan using PyRIT](./pyrit/README.md)

## Azure Resource Requirements
- [AI Red Teaming Agent](./azure-red-teaming-agent/README.md#infrastructure-setup)
- [PyRIT](./pyrit/README.md#infrastructure-setup)

## How to file issues and get help

This project uses GitHub Issues to track bugs and feature requests. Please search the existing issues before filing new ones to avoid duplicates. For new issues, file your bug report or feature request as a new issue.

For help and questions about using this project, please open a GitHub issue.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.

## Trademarks
This project may contain trademarks or logos for projects, products, or services.

Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft's Trademark & Brand Guidelines.

Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.

Any use of third-party trademarks or logos are subject to those third-party's policies.

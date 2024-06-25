 # jira-simple-lib
A tool to manage Jira with CLI.

# Badges

![Build Status](https://img.shields.io/github/actions/workflow/status/rimshaveritus/jira-simple-lib/main.yml?branch=JSL)
![License](https://img.shields.io/github/license/rimshaveritus/dummy-project)
![Last Commit](https://img.shields.io/github/last-commit/rimshaveritus/dummy-project)
![Issues](https://img.shields.io/github/issues/rimshaveritus/dummy-project)
![Stars](https://img.shields.io/github/stars/rimshaveritus/dummy-project)
[![codecov](https://codecov.io/gh/rimshaveritus/dummy-project/branch/main/graph/badge.svg)](https://codecov.io/gh/rimshaveritus)


## Getting Started Guide

This guide will help you get started with the Jira Simple Lib library.

## Table of Contents

- [Prerequisites](#Prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [API Reference](#api-reference)
- [License](#license)
- [Community](#community)

## Prerequisites

1. **Git Installation:** Ensure you have Git installed on your system. You can download and install it from [Git SCM](https://git-scm.com/).
2. **GitHub Account:** You must have a GitHub account to clone repositories.
3. **Python Installation:** Ensure you have Python installed on your system. You can download it from [Python.org](https://www.python.org/).
4. **API Token:** Instead of a password, you will use an API token for authentication.

## Installation

### Generate a GitHub API Token

1. Log in to your GitHub account.
2. Navigate to Settings (found by clicking your profile picture in the top right corner).
3. Go to Developer settings.
4. Select Personal access tokens and then Tokens (classic).
5. Click Generate new token.
6. Provide a note and select the scopes you need (at minimum, you might need repo scope).
7. Click Generate token.
8. Copy the generated token and store it securely. You will use this token in place of your password.

### Cloning the Repository

1. Open your terminal or command prompt.
2. Clone the repository using the provided link:
   ```sh
   git clone https://github.com/rimshaveritus/jira-simple-lib.git
3. Navigate to the cloned repository folder:
   cd jira-simple-lib
4. Check out the desired branch:
   git checkout JSL
**Installing Requirements and Running the Script**
1. Install the required Python packages:
   pip3 install -r requirements.txt
2. Run the main script:
   python3 ./jsl.py
3. If you don't have a config.json file, follow the prompts to enter your Jira URL, rimshaveritus, and API token:
    Enter Jira URL: https://jirasimplelib.atlassian.net
    Enter your rimshaveritus:
    Enter your Jira API token:
**Create your API Token**
1. Log in to Atlassian API Tokens.
2. Click Create API token.
3. From the dialog that appears, enter a memorable and concise label for your token.
**Note: For security reasons, it isn't possible to view the token after closing the creation dialog; if necessary, create a new token. You should store the token securely, just as for any password.**

## Usage

1. Use the --help option with any command to display usage information and available options:
```sh
python3 ./jsl.py --help
```
2. Refer to the documentation for detailed explanations of each command and additional usage examples.

## Contributing

(Details about how to contribute to the project, guidelines, and code of conduct)

## API Reference

(Detailed reference of the API provided by the library, including endpoints, request formats, and example responses)

## Lisence

(Information about the licensing of the library)

## Community

(Information about community forums, discussions, and where to seek help or provide feedback)




# Contributing to AyurFHIR Bridge

First off, thank you for considering contributing to AyurFHIR Bridge! This project is a community effort, and we welcome any contribution, from fixing a typo to adding a major new feature.

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please open an issue on our GitHub repository. A good bug report includes:
* A clear and descriptive title.
* A step-by-step description of how to reproduce the bug.
* The expected behavior and what happened instead.
* Screenshots, if applicable.

### Suggesting Enhancements
If you have an idea for a new feature or an improvement to an existing one, please open an issue. This allows us to discuss the idea before you spend time on the implementation.

### Submitting Code Changes (Pull Requests)
We love pull requests! Here’s the basic workflow:
1.  **Fork the repository** to your own GitHub account.
2.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/my-new-feature` or `git checkout -b fix/bug-description`.
3.  **Make your changes.** Please follow the existing code style.
4.  **Add tests** for your changes. This is important! We cannot merge code that is not tested.
5.  **Run the tests** locally to make sure everything is still working: `docker compose exec api pytest`.
6.  **Commit your changes** with a clear commit message.
7.  **Push your branch** to your fork.
8.  **Open a pull request** back to the main repository.

## Development Setup
The easiest way to get started is with Docker:
1.  Clone your fork of the repository.
2.  Run `docker compose up --build`.
3.  The API will be available at `http://localhost:8000`.

Thank you again for your contribution!
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Initial repository structure
- Initial documentation structure
- Initial roadmap
- Initial architecture vision
- ADR template
- First architectural decision record
- GitHub Project board
- Initial issues for M0 Foundation
- Local development environment validation document
- Docker support for the API
- Docker Compose configuration for local API execution
- Docker ignore file
- GitHub Actions CI pipeline for API tests
- Basic API request logging
- Basic API error handling
- README updates for M1 completion and M2 start
- LLM provider abstraction
- Fake LLM provider for local tests
- LLM message, response and usage models
- Requirement analysis prompt template
- Unit tests for requirement analysis prompt generation
- Structured requirement analysis schemas
- Requirement risk schema with severity validation
- Unit tests for requirement analysis schemas
- Portuguese-first requirement analysis defaults
- Requirement analyzer service
- Requirement analysis error handling
- Unit tests for requirement analyzer service
- LLM response parser for requirement analysis
- LLM response validation tests
- Strict schema validation for requirement analysis responses
- Retry configuration for requirement analysis
- Retry strategy for invalid LLM responses
- Fake LLM provider support for sequential responses
- Unit tests for requirement analysis retry behavior
- Fallback provider support for requirement analysis
- Fallback strategy for failed LLM responses
- Unit tests for requirement analysis fallback behavior
- Requirement analysis API endpoint
- Dependency provider for requirement analyzer service
- Fake structured response for local requirement analysis
- API tests for requirement analysis endpoint
- Environment-based settings for LLM provider selection
- `.env.example` file
- Settings tests for provider and retry configuration
- OpenAI LLM provider implementation
- LLM provider error handling
- Requirement analyzer support for provider-level failures
- Unit tests for OpenAI provider behavior
- Unit tests for provider error retry and fallback handling
- Ollama LLM provider implementation
- Environment settings for Ollama provider configuration
- Unit tests for Ollama provider behavior
- Documentation for local Ollama usage
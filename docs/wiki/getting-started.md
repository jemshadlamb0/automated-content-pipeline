# Getting started

## Requirements
- Python 3.11 or newer.
- Git and a virtual environment.
- Network access to install dependencies.
- For local model inference, sufficient RAM and disk for the selected Hugging Face model. Model weights must remain outside Git history.

## Install and validate
~~~bash
python -m venv .venv
# PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m acp.main --check-config
pytest
~~~

Optional inference libraries:
~~~bash
python -m pip install -e ".[huggingface]"
~~~

Review the model card, licence, target-language support, RAM requirements and quality before setting the model ID. A model ID alone does not pin immutable model contents; production deployments should pin an approved revision and verify the source.

## Select a language and niche
Edit config/settings.yaml:
- profile.niche: an ID under config/niches/.
- profile.language: an ID under config/languages/.
- profile.tone: an ID under config/tones/.
- profile.approach: an ID under config/approaches/.
- profile.region: the geographical focus.

Validate selections with the configuration command. Bihari and Rajasthani are family-level profiles and require a specific variety before use. Languages with ambiguous geographic centres require region selection.

## Safety defaults
Live publishing is disabled and dry-run is enabled. Do not enable live publication until source retrieval, tenant authorization, durable state, quotas and publisher error handling are implemented and tested. This repository foundation does not yet complete a real run.

## Troubleshooting
- Missing profile: check ID spelling and YAML filename.
- Invalid YAML: use spaces for indentation and validate quote/colon syntax.
- Model download or memory failure: choose a smaller reviewed model; be aware that clearing the cache requires a full download.
- Weak language quality: do not lower safety checks. Evaluate another model or require human approval.

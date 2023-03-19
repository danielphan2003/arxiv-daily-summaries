# arXiv Daily Summaries
This project creates an issue on every work day with the latest arXiv pre-prints matching a given set of keywords. It also creates a TL;DR summary automatically using [BART](https://huggingface.co/facebook/bart-base) by default.

# Configuration

In config.json file, you can specify:
- `arxiv_base`: The base URL to arXiv.org. Default to "https://arxiv.org".
- `sub_url`: Where to look for paper. Default to "https://arxiv.org/list/new/cs".
- `enable_emojis`: Whether to enable emojis or not. Default to False.
- `keywords`: List of keywords to look for in each papers. Those selected will get a generated summaries from the model in `model_name`.
- `assignees`: List of assignees whenever a new issue is created. Default to `os.environ['GITHUB_REPOSITORY_OWNER']`.
- `tldr_max_length`: Max length for the generated summaries.
- `model_name`: Model name for generating text.

## Usage

#### 1. Fork it to your repository on Github

#### 2. Update `config.json`

```json
{
  "enable_emojis": true,
  "keywords": ["iot"],
  "assignees": ["danielphan2003"],
  "tldr_max_length": 200
}
```

#### 3. Run a orkflow

To test the functionality, you can click "Run Workflow button" for an immediate run.


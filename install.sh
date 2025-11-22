#!/bin/bash

echo "Installing AI Autofixer..."

mkdir -p .github/workflows

cat > .github/workflows/ai-autofixer.yml <<EOF
name: AI Autofixer
on: [push]

jobs:
  code-check:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      # RUN YOUR ACTION
      - name: Run AI Scanner
        uses: Saachi30/autofixer-action@main

      # CREATE PR
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          token: \${{ secrets.GITHUB_TOKEN }}
          commit-message: "fix: AI fixed logic errors"
          branch: "autofix/logic-\${{ github.sha }}"
          title: "Autofixed Code"
          body: "I analyzed your code and found potential runtime errors. Here are the fixes."
EOF

echo "✅ Installed! Pushing code will now trigger the AI."
# install.ps1

Write-Host "🔮 Installing AI Logic Fixer for Windows..." -ForegroundColor Cyan

# 1. Create the workflows directory
$workflowDir = ".github\workflows"
if (-not (Test-Path -Path $workflowDir)) {
    New-Item -ItemType Directory -Path $workflowDir | Out-Null
}

# 2. Define the YAML content
# MAKE SURE TO REPLACE 'your-github-username' BELOW
$yamlContent = @"
name: AI Logic Fixer
on: [push]

jobs:
  logic-check:
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
        uses: your-github-username/autofix-action@main

      # CREATE PR
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          token: `${{ secrets.GITHUB_TOKEN }}
          commit-message: "fix: AI fixed logic errors"
          branch: "autofix/logic-`${{ github.sha }}"
          title: "🧠 AI Logic Fixes"
          body: "I analyzed your code and found potential runtime errors. Here are the fixes."
"@

# 3. Write the file
$filePath = "$workflowDir\ai-logic-fix.yml"
Set-Content -Path $filePath -Value $yamlContent

Write-Host "✅ Installed! Pushing code will now trigger the AI." -ForegroundColor Green
name: update funds

on:
  schedule:
    - cron: "0 18 * * 1-5"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  run:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install packages
        run: |
          python -m pip install --upgrade pip
          pip install pandas lxml html5lib beautifulsoup4

      - name: Run update script
        run: |
          python script/update_db.py

      - name: Show git status
        run: |
          git status
          ls -l data || dir data

      - name: Commit and push if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/pension.db
          if git diff --cached --quiet; then
            echo "Geen wijzigingen"
          else
            git commit -m "Update pension.db"
            git push origin HEAD:main
          fi

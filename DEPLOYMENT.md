# Deployment handoff

## Canonical source
- GitHub: https://github.com/mleuatd/dtx-drum-flow
- Branch: main
- Site source: `site/`

## Automatic public mirror
A GitHub Pages deployment workflow is stored at:
`.github/workflows/deploy-site.yml`

Once GitHub Pages is enabled for this repository with **Source = GitHub Actions**, every change to `main/site/**` deploys automatically.

Expected public mirror URL:
https://mleuatd.github.io/dtx-drum-flow/

## Existing ChatGPT Site
Current URL:
https://dtx-drum-flow.mleuatd.chatgpt.site

This URL is owned by ChatGPT Sites and cannot be rerouted by the normal-chat GitHub connector.

To update the SAME ChatGPT Site URL, use Work/Sites and publish a new version of the existing Site. Official Sites behavior keeps the same Site URL when an updated version is published.

### One-command handoff for Work
Use this instruction in Work:

> DTX Drum Flow を編集してください。共有GitHubリポジトリ `mleuatd/dtx-drum-flow` の `main/site/` を現在の基準ソースとして取り込み、既存Site `appgprj_6aa76fd7a1e48191b27d3b4793a85e70` を更新してください。新しいSiteを作らず、既存の `https://dtx-drum-flow.mleuatd.chatgpt.site` に新バージョンとして公開してください。GitHubのmainを変更した場合はコミット履歴も維持してください。

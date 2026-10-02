# GitHub 发布与恢复

建议新仓库名：`godot-agent-skills`，拥有者 `alexliyu7352`，默认私有。此文件是发布指引，不代表该远端仓库已创建。

本次连接器能识别 GitHub 账户并操作已有授权仓库，但没有创建仓库接口；已授权 Desktop Commander 设备离线。本次不借用/修改任何旧仓库，不索要或输出访问令牌。

## 本地已有登录的 GitHub CLI 时
完整源包解压在独立目录，确认内容和测试后：

```bash
# 如果来自源码 ZIP 且尚无 .git：
git init -b main
git add .
git commit -m "feat: add curated Godot agent skills preview"

# 由你本机已经登录的 gh 创建私有新仓库并推送。
gh repo create alexliyu7352/godot-agent-skills --private --source . --remote origin --push
```

若仓库已经存在，不再次 create。核实 origin 指向你刚创建的正确空仓库后再 push，不使用 force。通过 ChatGPT GitHub 连接器发布时，需先创建空仓库并使当前 GitHub App 获得该仓库访问；新仓库不一定自动包含在“仅选定仓库”的授权中。

## Git bundle 恢复
交付中若包含 `.bundle`，可 `git clone /absolute/path/to/file.bundle godot-agent-skills` 恢复本地提交与全部已跟踪文件；bundle 的 origin 是本地文件，不能直接当成 GitHub 远端。确认新的 GitHub 仓库后替换 origin，再正常推送。

源码 ZIP 不包含 .git，bundle 包含历史；两者都不包含账号凭据或现有游戏代码。SHA256SUMS 用于传输校验，不是签名。推送后重新读取默认分支与提交哈希核对，GitHub CI 的实际结果需另行确认。

官方 CLI 用法：https://cli.github.com/manual/gh_repo_create

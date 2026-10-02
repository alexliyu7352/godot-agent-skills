# 发布状态与恢复

仓库 `alexliyu7352/godot-agent-skills` 已由用户创建并公开。preview.1 已发布到 main，基线提交 `c3b29e54abe930fd10abd8d15389e4b58d5e6a1e`，目录树 `19075fca180f41b1493862446908300d9577121b`。无需再次创建仓库或重新提供凭据。

## 本次 preview.2

完整修订保存在源码 ZIP、Git bundle 和补丁中。GitHub 工具对 `tools/validate.py` 写入连续返回无法确定安全状态，因此本次未发布完整版本，未改变 main；没有通过另一个接口或编码上传来绕过。

`test/review-godot-contracts` 是独立引擎验证分支，只包含能够正常写入的示例、夹具和相关工具。它的 README 明确标识非完整版本。不得因为它的 CI 通过，就把它合入 main 或当作精简包安装。

## 恢复完整本地成果

源码 ZIP 不含 .git，可解压到独立目录运行验证。Git bundle 包含历史和完整修订分支，可用：

```bash
git clone /absolute/path/to/godot-agent-skills-0.1.0-preview.2.bundle recovered-skills
```

bundle 的 origin 是本地文件，不是 GitHub。其 preview.1 基线来自制作时的本地提交，和 GitHub preview.1 的提交 ID 不同，但目录树完全一致；不要为使历史一致强推覆盖远端。

另附补丁以与远端基线完全一致的目录树生成，可在基线的干净工作副本中审核和检查适用性。它不是自动发布脚本。将来的正式发布需要正常授权写入、复核远端状态、重新运行相应检查，并保留历史；本次没有声称该步骤已完成。

所有交付物只包含 Skills、工具、测试和非敏感证据，不包含用户游戏或账户凭据。SHA-256 用于传输完整性，不是数字签名。测试与证据范围见 [验证报告](TEST_REPORT.md)。

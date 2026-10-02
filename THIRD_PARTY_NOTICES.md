# 上游来源与许可

本包是重新组织、纠错和裁剪后的衍生整合，不是三套框架原样拼接。

| 上游 | 许可 | 保留内容 |
|---|---|---|
| gamedev-skills/awesome-gamedev-agent-skills | Apache-2.0 | 领域知识结构及专业方法的适配；原 NOTICE 保留 |
| jame581/GodotPrompter | MIT | 调试、信号和性能定位的精选方法；保留完整许可 |
| liangdabiao/Godogen（继承 Alex Ermolov 的 Godogen） | MIT | 场景 owner、打包和重载验证方法；不带原生成工作流或外部服务脚本 |

完整提交、源路径、目标模块和本地处理见 `sources.lock.json`。
原许可位于 `licenses/`；新整合采用根目录 `LICENSE` 的 Apache-2.0。
每个可安装技能含完整 `LICENSE.txt`，所以按技能复制也保留必要法律文本。
这是分发需要，不是要求 Agent 每次加载许可证正文。
原 NOTICE 关于“original works”的表述仅描述该上游，不能用于声称本整合完全没有衍生内容。

未导入的旧总入口、多代理定义、固定模型配置、原安装/发布脚本及资产生成 API 不属于本包。
没有附带游戏美术、字体、用户项目源码、账号密钥或第三方模型凭据。

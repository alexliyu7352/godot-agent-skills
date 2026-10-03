# 分层场所与交互坐标

只用于新场所、场景美术层级或热点接入；保留项目已经采用的节点与相机方案。下面是一个可选组织，不是要求重建全部游戏。

```text
LocationRoot                 # 这个场所的运行实例
  World                      # Node2D，随场景相机变化
    Background               # 不含需独立变化对象的绘景
    Actors                   # 按世界状态决定在场与交互
    Props                    # 文书、门、货物等
    Foreground               # 有意遮挡，不抢输入
    InteractionTargets       # Area2D 或项目已有目标系统
  HUD                        # CanvasLayer 或固定屏幕 Control
    ContextHint
    Dialogue                 # 临时显隐，不替换整个 LocationRoot
```

固定绘景也可以用 Control + TextureRect 加热点，但不要误把它称为全部对象可独立移动的世界。只在视差、时间变化或人物日程需要时拆分相应层；不要机械要求每个静止道具都独立纹理。全局状态在既有状态层，场景读取并呈现，不能让未加载城镇的人物停止结算。

## 可观察的构图约束
人物坐姿/脚底接地点与桌椅地面相符；前景不能切断主交互者脸和手；出口在允许的画面裁切下仍能辨认。主体和背景光向一致，不靠额外发光轮廓补救错误素材。主角的近景立绘与在场角色应保持身份、衣色与视角逻辑。

## 绘景与热点只维护一套变换
如果采用保持比例覆盖，给定源图大小 S 和目标矩形 V：

```text
scale = max(V.width / S.width, V.height / S.height)
offset = (V.size - S * scale) / 2
screen_point = V.position + offset + source_point * scale
```

这描述的是居中 cover；letterbox 应使用 min，且黑边不接受场景点击。将点击逆变换回源图后做热点命中，或用同一个父节点变换视觉与热点。不要分别“差不多”放置它们。Node2D + Camera2D 应使用引擎坐标转换而不是再手算第二份。TextureRect 的覆盖会裁切边缘，布局与热点必须一起验证。[API 说明](https://docs.godotengine.org/en/4.6/classes/class_texturerect.html)。

## 状态连续性
打开对话不重新实例化整个场所；关闭后还原原目标焦点，而不是空白页面。若对话期间人物离开、目标失效或场景卸载，取消对应输入和补间，并清楚反馈。灯光、尘埃等装饰不是世界状态提交信号。

## 最小运行检查
从实际在场人物进入一次交互，改变一条可观察状态，再关闭并重新进入；确认对象位置、已改变状态与焦点。素材尺寸/裁切改变时加边缘目标检查；场景保存方式改变时补磁盘重载，不重复全部玩法测试。技术检查不能证明美术达到目标。

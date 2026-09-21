# digital-gua — 数字卦起卦解卦 Skill

给 AI 编程助手（Kiro / Claude Code / Codex 等支持 SKILL.md 的工具）用的数字卦 skill。
起卦和查表由脚本完成，模型只负责解读，避免口算出错和编造经文。

## 安装

需要 Python 3.8+（终端输 `python --version` 检查），无第三方依赖。

**方式一：git clone（推荐，以后 `git pull` 即可更新）**

Windows PowerShell：

```powershell
git clone https://github.com/szktc/digital-gua.git $env:USERPROFILE\.kiro\skills\digital-gua
```

Mac / Linux：

```bash
git clone https://github.com/szktc/digital-gua.git ~/.kiro/skills/digital-gua
```

用 Claude Code 的把路径里的 `.kiro` 换成 `.claude`。

**方式二：下载 ZIP**

仓库页面点 **Code → Download ZIP**，解压，把文件夹改名为 `digital-gua`（去掉 `-main` 后缀），放到下表对应目录：

| 工具 | 目录 |
|------|------|
| Kiro（全局，所有项目可用） | `~/.kiro/skills/digital-gua/` |
| Kiro（项目级） | `<项目>/.kiro/skills/digital-gua/` |
| Claude Code（全局） | `~/.claude/skills/digital-gua/` |
| Claude Code（项目级） | `<项目>/.claude/skills/digital-gua/` |

Windows 上 `~` 就是 `C:\Users\<你的用户名>`，在资源管理器地址栏输入 `%USERPROFILE%\.kiro\skills` 可直接打开；`skills` 文件夹不存在就新建一个。

装好后**新开一个会话**才会加载，旧会话不认。

## 用法

对助手说任何一句：

> 帮我算算换工作顺不顺。
> 我想占一卦。
> 周易 / 易经 / 数字卦 / 起卦 / 卦象……

第一次触发时，助手会先说明数字卦是什么、怎么起卦、什么能问什么不能问（三不占）、为什么不要迷信它。你回复"了解，开始"，再给出问题和随手写的三组三位数，助手才会运行 `scripts/cast.py` 起卦，按六段输出：起卦过程、卦象校验、三法汇解、趋势判断、行动建议、风险提示，最后附一段提醒。

## 联系作者

对经文和义理的解读有疑问，欢迎交流：微信 davideweixinhao。
（联系方式配置在 `SKILL.md` frontmatter 的 `author_contact`，以及第五步结尾提示里，改时两处一起改。）

也可以直接用脚本：

```bash
python scripts/cast.py 372 815 246              # 三数起卦，输出 JSON
python scripts/cast.py 372 815 246 --order upper-first   # 第一组定上卦
python scripts/cast.py --lookup 水雷屯           # 查单卦原文
python scripts/cast.py --lookup 3
```

## 起卦规则

傅佩荣数字卦法：第一组 %8 定下卦，第二组 %8 定上卦，第三组 %6 定动爻。
余数 0 记为 8（坤）和 6（上爻）。先天八卦数：乾1 兑2 离3 震4 巽5 坎6 艮7 坤8。

## 文件

```
digital-gua/
├── SKILL.md                 # 给模型的流程与规则
├── README.md
├── scripts/cast.py          # 起卦、变卦、互卦、错综卦、校验
└── references/
    ├── intro.md             # 起卦前给用户的说明：是什么、怎么用、三不占、别迷信
    ├── hexagrams.json       # 64 卦卦辞、大象、384 爻辞（通行本，公版）
    └── rules.md             # 解卦优先级、爻位、互卦读法、断语说明
```

## 说明

- `hexagrams.json` 只收《周易》经文，不含《高岛易断》或傅佩荣著作原文。SKILL.md 要求模型把这两者作为"方法视角"使用，不得伪造引文。
- 内容仅供思考参考，不构成医疗、法律、投资建议。

# tests/ 使用规约

## verify 脚本规范

- 仓根定位一律相对：`sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`，
  禁止硬编码盘符绝对路径（§68 基建：硬编码使 worktree 跨版本对拍失效）。
- 一次性探针归档至 `fixtures/`（硬编码路径在该目录豁免，见其 README）。

## 对拍检查清单（§69 方法论，2026-10-12）

目的：验证「当前 verify 断言在基线 modules 上是否通过」。**只让 modules 变化，
verify 必须保持当前版**。

1. **verify 是当前版？** worktree checkout 出来的是旧版 verify——须从当前 HEAD
   拷贝当前版 verify 进 worktree 再运行（§69 实证：806e6ff 对拍曾因用旧版
   verify 而"双错抵消"，误判 marriage 3 项"自引入即失败"）。
2. **modules 是基线版？** verify 的仓根定位必须指向 worktree 根
   （相对定位天然满足；硬编码路径会导入主仓 modules，对拍无效）。
3. **退出码+签名双录**：记录基线与当前的 FAIL 项名与 detail 签名，逐字比对。
4. **双错抵消自查**：对拍前先跑一次「当前 verify + 当前 modules」确认已知
   状态（如当前应 FAIL 的项在基线上翻绿才有意义）。

历史上四次误判均源于方法缺陷而非事实多变（§69.1）：B6 对拍"碰巧成立"、
D2-4c"自引入即失配"、README 误覆盖归因行尾、marriage"自引入即失败"——
凡对拍结论，先过本清单。

> **TODO（§69 验收拍板 P2）**：本清单未来脚本化——形态=「对拍前置脚本」
> （自动完成：拷当前 verify 进 worktree + 跑双错抵消自查），非全自动
> verify_baseline.sh（基线 commit 的选择需人工判断，不应被脚本掩盖）。

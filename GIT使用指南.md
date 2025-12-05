# GitHub仓库本地操作完整指南

## 项目状态

✅ **已完成的配置**：
- Git仓库已初始化
- 已连接到GitHub远程仓库：`https://github.com/zhenyuren/1999-2023companyDEIndex.git`
- 已获取远程分支信息
- 已创建详细的README.md文档

## 第一步：设置Git用户信息（必须）

在进行任何Git操作之前，请先设置您的Git用户信息。这将记录谁进行了代码修改。

打开终端，在当前项目目录下运行：

```bash
# 设置用户名
git config user.name "您的GitHub用户名"

# 设置邮箱
git config user.email "您的GitHub邮箱"
```

如果您希望在所有Git项目中使用相同的用户信息，可以添加`--global`选项：

```bash
git config --global user.name "您的GitHub用户名"
git config --global user.email "您的GitHub邮箱"
```

## 第二步：修改文件

您现在可以在当前目录（`/Users/dudu/Desktop/智能金融学院/数据实验/数据经济指数/`）中修改以下文件：

- `digital_transformation_dashboard.py` - Streamlit应用主程序
- `digital_transformation_index.py` - 数字化转型指数计算脚本
- `1999-2023年数字化转型指数结果表.csv` - 数字化转型指数结果数据文件

您也可以添加新文件到这个目录中。

## 第三步：提交修改到本地Git仓库

当您完成文件修改后，需要将这些更改提交到本地Git仓库：

1. 查看修改的文件（确认哪些文件被修改了）：
   ```bash
   git status
   ```

2. 添加所有修改的文件：
   ```bash
   git add .
   ```

3. 提交更改并添加描述信息：
   ```bash
   git commit -m "描述您的修改内容"
   ```
   例如：`git commit -m "更新应用界面，添加新的查询功能"`

## 第四步：推送到GitHub远程仓库

提交到本地仓库后，需要将这些更改推送到GitHub：

```bash
# 首次推送时使用（只需要执行一次）
git push -u origin main

# 后续推送时可以简化为
git push origin main
```

## 第五步：从GitHub拉取最新更新

当您需要获取GitHub仓库中的最新更改时：

```bash
git pull origin main
```

## 常见问题解决

### 1. 推送失败，提示冲突

如果推送失败并提示有冲突，请执行以下步骤：

```bash
# 拉取远程代码并尝试自动合并
git pull --rebase origin main
```

如果出现冲突，您需要手动编辑冲突文件，然后：

```bash
git add 冲突的文件名
git rebase --continue
git push origin main
```

### 2. 权限被拒绝

如果提示权限被拒绝，可能是以下原因：
- 您没有仓库的写入权限
- 需要配置SSH密钥

请检查您的GitHub账户是否有权限访问该仓库。

### 3. 查看仓库状态

随时查看仓库当前状态：

```bash
# 查看当前状态
git status

# 查看远程配置
git remote -v

# 查看分支
git branch -a
```

## 运行Streamlit应用

修改代码后，您可以随时运行应用来测试：

```bash
streamlit run digital_economy_app.py
```

## 重要提示

1. **定期提交**：养成定期提交代码的习惯，每次提交应该有明确的目的
2. **先拉后推**：推送前先拉取最新代码，避免冲突
3. **合理的提交信息**：写清楚每次提交做了什么修改
4. **保持.gitignore正确**：确保敏感数据和大文件不会被提交

祝您使用愉快！如有任何问题，请参考Git官方文档或GitHub帮助中心。
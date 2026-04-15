# Vue 3 + Vuetify 3 前端构建脚本

## 开发模式

```bash
cd frontend
npm install
npm run dev
```

后端需要单独运行:
```bash
uv run pipui
```

## 生产构建

```bash
cd frontend
npm install
npm run build
```

然后启动后端:
```bash
uv run pipui
```

## 使用构建命令 (需要 hatch)

```bash
uv run hatch run build-frontend
```

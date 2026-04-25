# Docker Templates

这份文档只解决一件事：项目技术栈确认后，快速决定该用哪套 Docker 模板。

## 使用原则

- 不追求万能 Dockerfile。
- 先判断项目类型，再套对应模板。
- Docker 统一的是交付方式，不统一项目运行方式。
- 项目还在起步阶段时，不必急着写 Docker。

## 怎么选

### 1. 静态前端

满足下面大部分情况时，选这一套：

- 项目构建后输出 `dist` 或 `build`
- 线上只需要静态文件
- 不需要 Node 常驻运行
- 常见于 Vite、React 静态站、Vue 静态站

适合：

- 官网
- 展示站
- 工具页
- 作品集

不适合：

- 需要服务端渲染
- 需要后端接口
- 需要定时任务或服务常驻

#### Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
```

#### docker-compose.yml

```yaml
services:
  web:
    build: .
    ports:
      - "8080:80"
    restart: always
```

#### 部署特点

- 先构建，再交给 `nginx` 容器托管
- `1Panel` 反向代理到容器端口
- 不需要 Node 常驻进程

## 2. Next.js

满足下面大部分情况时，选这一套：

- 项目依赖 `next`
- 有 `next.config.*`
- 有 `app/` 或 `pages/`
- 需要 SSR、服务端路由、API Route

适合：

- 需要 SEO 的站点
- 带后台接口的前端应用
- 有服务端渲染需求的项目

不适合：

- 纯静态展示且不需要 Next 特性
- 只是一个简单静态页面

#### Dockerfile

```dockerfile
FROM node:20-alpine AS deps

WORKDIR /app

COPY package*.json ./
RUN npm install

FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app ./

EXPOSE 3000

CMD ["npm", "start"]
```

#### docker-compose.yml

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    env_file:
      - .env
    restart: always
```

#### 部署特点

- 需要 Node 常驻运行
- `1Panel` 通常反向代理到 `3000`
- `.env`、上传目录、数据库连接要单独管理

## 3. Node 服务

满足下面大部分情况时，选这一套：

- 项目本质是接口服务
- 依赖 `express`、`koa`、`nestjs`、`fastify` 等
- 服务需要长期监听一个端口
- 前后端分离，当前项目只负责后端

适合：

- API 服务
- 管理后台后端
- Webhook 服务
- 定时任务服务

不适合：

- 纯静态站
- 主要是服务端页面渲染且已经是 Next.js

#### Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

#### docker-compose.yml

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    env_file:
      - .env
    restart: always
```

#### 部署特点

- 服务常驻运行
- 常见做法是由 `1Panel` 反代到容器端口
- 如果依赖 MySQL、PostgreSQL、Redis，可以继续扩展 `docker-compose.yml`

## 什么时候不用急着写 Docker

先别写 Docker 的典型情况：

- 项目还在验证阶段
- 技术栈还没确定
- 只是本地快速开发
- 只是一个临时实验项目

这时候先保留：

- `package.json`
- `.env.example`
- 基础启动方式

等项目准备上线或准备长期维护时，再补 Docker。

## 什么时候该补 Docker

出现下面情况时，就可以开始补：

- 项目准备上线
- 技术栈已经稳定
- 需要迁移到其他机器
- 需要标准化部署
- 需要自动部署
- 已经被环境差异坑过

## 默认决策

以后确认技术栈后，直接按这条规则走：

- 纯静态产物：用静态前端模板
- 有 `next` 且需要服务端能力：用 Next.js 模板
- 是后端接口服务：用 Node 服务模板

如果后面项目本来就自带 `Dockerfile` 或 `docker-compose.yml`，优先按项目自身结构处理，不强行套模板。

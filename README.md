
# 这是我的基于FLask+Vue.js 前后分离实现的微型博客

## 1.如何使用
git clone https://github.com/Sunnywillow/vueflasky-myblog.git

## 2.后端Backend
$ mkdir backend / cd backend  在命令行中先创建一个文件夹

$ python -m venv venv  创建python3虚拟环境

$ venv\Scripts\activate Windows系统 激活虚拟环境 (Linux:source venv/bin/activate)

(venv)$ pip install -r requirements.txt

### 使用Flask-migrate创建数据库迁移脚本

(venv)$ flask db upgrade

### 创建一个.env环境变量文件

FLASK_APP=madblog.py
FLASK_DEBUG=1

(venv)$ flask run

## 3.前端frontend
$ cd front-end
$ npm install
$ npm run dev

浏览器访问: http://localhost:8080


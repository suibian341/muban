#!/usr/bin/env python3
"""
创建开发者账号种子数据
运行: python seed_dev_user.py
"""
import os
import sys

# 确保从当前目录导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def create_dev_user():
    app = create_app()
    with app.app_context():
        # 检查是否已存在
        dev = User.query.filter_by(username='suibian341').first()
        if dev:
            print('[INFO] Dev user already exists')
            print('  Username: suibian341')
            return

        # 创建开发者账号
        dev = User(
            username='suibian341',
            password_hash=generate_password_hash('135260352'),
            role='dev',
            email='dev@example.com',
            company_name='Developer',
            is_active=True
        )
        db.session.add(dev)
        db.session.commit()
        print('[OK] Dev user created successfully')
        print('  Username: suibian341')
        print('  Password: 135260352')
        print('  Role: dev')

if __name__ == '__main__':
    create_dev_user()

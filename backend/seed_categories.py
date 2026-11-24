#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seed script: populate full category tree."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, Category

CATEGORIES = [
    # (parent_name_en, name, name_en, icon, sort_order)
    # ── 产品分类（只放真正的产品类目） ──
    (None, '玩具全品类', 'Toys', '🧸', 1),
    (None, '无人机类', 'Drones', '🚁', 2),
    (None, '小家电', 'Home Appliances', '🔌', 3),

    # ── Toys children ──
    ('Toys', '益智早教玩具', 'Educational Toys', '🧩', 1),
    ('Toys', '遥控玩具', 'RC Toys', '🎮', 2),
    ('Toys', '玩具无人机', 'Drones', '🛸', 3),
    ('Toys', '娃娃公仔/毛绒玩具', 'Dolls & Plush Toys', '🧸', 4),
    ('Toys', '积木拼装玩具', 'Building Blocks', '🏗️', 5),
    ('Toys', '过家家玩具', 'Pretend Play', '🍳', 6),
    ('Toys', '音乐玩具', 'Musical Toys', '🎵', 7),
    ('Toys', '户外玩具', 'Outdoor Toys', '🏖️', 8),
    ('Toys', '婴幼儿玩具', 'Baby Toys', '👶', 9),
    ('Toys', '彩绘DIY玩具', 'Paint & Art Toys', '🎨', 10),
    ('Toys', '新奇小玩具/礼品玩具', 'Novelty Toys', '🎁', 11),
    ('Toys', '派对玩具', 'Party Toys', '🎉', 12),
    ('Toys', '角色扮演玩具', 'Role Play Toys', '🦸', 13),
    ('Toys', '电动玩具', 'B/O Toys', '🔋', 14),
    ('Toys', '其他玩具', 'Other Toys', '📦', 15),

    # ── Drones children ──
    ('Drones', '迷你无人机', 'Mini Drones', '🤏', 1),
    ('Drones', '遥控无人机', 'RC Drones', '🎮', 2),
    ('Drones', '航拍无人机', 'Camera Drones', '📷', 3),
    ('Drones', 'DIY组装无人机', 'DIY Drones', '🔧', 4),

    # ── Home Appliances children ──
    ('Home Appliances', '美容个护工具', 'Beauty Tools', '💄', 1),
    ('Home Appliances', '家居小电器', 'Home Electronics', '🏠', 2),
    ('Home Appliances', '数码配件', 'Digital Gadgets', '📱', 3),
]

# 营销专区（不作为产品分类，通过产品标记实现）：
# - 新品专区 New Arrivals → products.is_new = True
# - 爆款专区 Hot Sale → products.is_featured = True
# - 清仓库存 Clearance Stock → products.is_clearance = True（独立页面 /clearance）


def seed():
    app = create_app()
    with app.app_context():
        # Build lookup: name_en -> id for parents
        parent_map = {}

        for parent_en, name, name_en, icon, sort_order in CATEGORIES:
            if parent_en is None:
                # Top-level category
                existing = Category.query.filter_by(name_en=name_en, parent_id=None).first()
                if existing:
                    existing.name = name
                    existing.icon = icon
                    existing.sort_order = sort_order
                    parent_map[name_en] = existing.id
                    print(f'[UPDATE] {name_en} ({name})')
                else:
                    cat = Category(name=name, name_en=name_en, icon=icon, sort_order=sort_order, parent_id=None)
                    db.session.add(cat)
                    db.session.flush()
                    parent_map[name_en] = cat.id
                    print(f'[NEW]    {name_en} ({name})')
            else:
                pid = parent_map.get(parent_en)
                if not pid:
                    print(f'[SKIP]   Parent "{parent_en}" not found for {name_en}')
                    continue
                existing = Category.query.filter_by(name_en=name_en, parent_id=pid).first()
                if existing:
                    existing.name = name
                    existing.icon = icon
                    existing.sort_order = sort_order
                    print(f'[UPDATE] {parent_en} > {name_en} ({name})')
                else:
                    cat = Category(name=name, name_en=name_en, icon=icon, sort_order=sort_order, parent_id=pid)
                    db.session.add(cat)
                    print(f'[NEW]    {parent_en} > {name_en} ({name})')

        db.session.commit()

        # Deactivate marketing categories if they exist in DB (they shouldn't be product categories)
        marketing_names = ['New Arrivals', 'Hot Sale', 'Clearance Stock']
        for mname in marketing_names:
            old = Category.query.filter_by(name_en=mname, parent_id=None).first()
            if old:
                # Deactivate parent and its children
                for child in old.children:
                    child.is_active = False
                old.is_active = False
                print(f'[DEACTIVATE] {mname} (marketing zone, not a product category)')
        db.session.commit()

        print('\nDone! Category tree:')
        tops = Category.query.filter_by(parent_id=None).order_by(Category.sort_order).all()
        for t in tops:
            print(f'  {t.icon} {t.name_en} ({t.name})')
            for c in sorted(t.children, key=lambda x: x.sort_order):
                print(f'      {c.icon} {c.name_en} ({c.name})')


if __name__ == '__main__':
    seed()

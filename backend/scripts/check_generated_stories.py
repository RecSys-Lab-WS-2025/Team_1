#!/usr/bin/env python3
"""
查询数据库中已生成故事的路线
使用方法: python backend/scripts/check_generated_stories.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import init_db, get_db_session
from app.models.entities import Route, Breakpoint


async def check_generated_stories():
    """查询并显示所有已生成故事的路线"""
    print("=" * 80)
    print("📖 查询数据库中已生成的故事")
    print("=" * 80)
    
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = await get_db_session()
    
    try:
        # 查询所有有故事的路线
        result = await db.execute(
            select(Route)
            .where(Route.story_prologue_body.isnot(None))
            .options(selectinload(Route.breakpoints))
            .order_by(Route.id)
        )
        routes_with_stories = result.scalars().all()
        
        # 统计信息
        total_result = await db.execute(
            select(func.count(Route.id))
        )
        total_routes = total_result.scalar() or 0
        
        print(f"\n📊 统计信息:")
        print(f"   总路线数: {total_routes}")
        print(f"   已生成故事的路线数: {len(routes_with_stories)}")
        print(f"   未生成故事的路线数: {total_routes - len(routes_with_stories)}")
        
        if routes_with_stories:
            print(f"\n✅ 已生成故事的路线列表:")
            print("-" * 80)
            for i, route in enumerate(routes_with_stories, 1):
                # 统计 breakpoint 数量
                bp_count = len(route.breakpoints) if route.breakpoints else 0
                
                # 统计有 main_quest_snippet 的 breakpoint 数量
                bp_with_story = 0
                if route.breakpoints:
                    bp_with_story = sum(
                        1 for bp in route.breakpoints 
                        if bp.main_quest_snippet
                    )
                
                # 计算故事内容长度
                prologue_len = len(route.story_prologue_body) if route.story_prologue_body else 0
                epilogue_len = len(route.story_epilogue_body) if route.story_epilogue_body else 0
                
                print(f"\n{i}. 路线 ID: {route.id}")
                print(f"   标题: {route.title}")
                if route.story_prologue_title:
                    print(f"   故事标题: {route.story_prologue_title}")
                print(f"   位置: {route.location or 'N/A'}")
                print(f"   难度: {route.difficulty or 'N/A'}")
                print(f"   长度: {route.length_meters/1000:.2f} km" if route.length_meters else "   长度: N/A")
                print(f"   Breakpoints: {bp_count} 个 (其中 {bp_with_story} 个有章节内容)")
                print(f"   序章长度: {prologue_len} 字符")
                print(f"   尾声长度: {epilogue_len} 字符")
                
                # 显示序章预览
                if route.story_prologue_body:
                    preview = route.story_prologue_body[:100].replace('\n', ' ')
                    print(f"   序章预览: {preview}...")
        else:
            print("\n❌ 数据库中没有已生成的故事")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(check_generated_stories())




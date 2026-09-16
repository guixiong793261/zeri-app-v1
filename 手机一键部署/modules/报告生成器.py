# -*- coding: utf-8 -*-
"""
================================================================================
择日报告生成器
================================================================================
生成专业的择日报告，支持文本、HTML和PDF格式

使用方法:
    from modules.报告生成器 import generate_report
    report = generate_report(results, event_type, shan_xiang, owners)
    report.save_text(filename)
    report.save_html(filename)
================================================================================
"""

import os
import sys
from datetime import datetime


class ReportGenerator:
    """择日报告生成器"""
    
    def __init__(self, event_type, start_date, end_date, shan_xiang=None, owners=None):
        """初始化报告生成器
        
        Args:
            event_type: 事项类型
            start_date: 开始日期
            end_date: 结束日期
            shan_xiang: 山向
            owners: 事主信息
        """
        self.event_type = event_type
        self.start_date = start_date
        self.end_date = end_date
        self.shan_xiang = shan_xiang
        self.owners = owners or []
        self.results = []
        self.generate_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def add_results(self, results):
        """添加择日结果
        
        Args:
            results: 择日结果列表
        """
        self.results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    
    def generate_text_report(self):
        """生成纯文本报告
        
        Returns:
            str: 纯文本格式的报告
        """
        lines = []
        
        # 报告头部
        lines.append("=" * 80)
        lines.append("专业级正五行择日报告")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"生成时间：{self.generate_time}")
        lines.append(f"事项类型：{self.event_type}")
        lines.append(f"日期范围：{self.start_date} 至 {self.end_date}")
        if self.shan_xiang:
            lines.append(f"山向：{self.shan_xiang}")
        
        if self.owners:
            lines.append("")
            lines.append("【事主信息】")
            for owner in self.owners:
                name = owner.get('name', '事主')
                zodiac = owner.get('生肖', '')
                gender = owner.get('性别', '')
                lines.append(f"  - {name}（{gender}，{zodiac}）")
        
        # 统计信息
        total_count = len(self.results)
        good_count = sum(1 for r in self.results if r.get('score', 0) >= 100)
        bad_count = sum(1 for r in self.results if r.get('score', 0) < 60)
        
        lines.append("")
        lines.append("【统计信息】")
        lines.append(f"  - 总天数：{total_count} 天")
        lines.append(f"  - 吉日（≥100分）：{good_count} 天")
        lines.append(f"  - 凶日（<60分）：{bad_count} 天")
        
        # 详细结果
        lines.append("")
        lines.append("=" * 80)
        lines.append("详细择日结果（按评分排序）")
        lines.append("=" * 80)
        
        for i, result in enumerate(self.results, 1):
            score = result.get('score', 0)
            level = result.get('level', '-')
            date_str = result.get('date', '-')
            sizhu = result.get('sizhu', {})
            
            lines.append("")
            lines.append(f"【第{i}名】 {date_str}")
            lines.append("-" * 60)
            
            if isinstance(sizhu, dict):
                lines.append(f"  四柱：{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}")
                lines.append(f"  天干：{sizhu.get('year_gan', '')}({sizhu.get('year_zhi', '')}) {sizhu.get('month_gan', '')}({sizhu.get('month_zhi', '')}) {sizhu.get('day_gan', '')}({sizhu.get('day_zhi', '')}) {sizhu.get('hour_gan', '')}({sizhu.get('hour_zhi', '')})")
            elif isinstance(sizhu, str):
                lines.append(f"  四柱：{sizhu}")
            
            lines.append(f"  评分：{score} 分 | 等级：{level}")
            
            # 宜忌
            yi_list = result.get('yi_list', [])
            ji_list = result.get('ji_list', [])
            if yi_list:
                lines.append(f"  宜：{'、'.join(yi_list[:5])}")
            if ji_list:
                lines.append(f"  忌：{'、'.join(ji_list[:3])}")
            
            # 神煞详情
            shensha_list = result.get('shensha_list', [])
            if shensha_list:
                yi_shensha = [s for s in shensha_list if isinstance(s, dict) and s.get('score', 0) > 0]
                ji_shensha = [s for s in shensha_list if isinstance(s, dict) and s.get('score', 0) < 0]
                
                if yi_shensha:
                    lines.append("  吉神：")
                    for s in yi_shensha[:3]:
                        lines.append(f"    ✅ {s.get('name', '')} (+{s.get('score', 0)}分)")
                
                if ji_shensha:
                    lines.append("  凶煞：")
                    for s in ji_shensha[:3]:
                        lines.append(f"    ❌ {s.get('name', '')} ({s.get('score', 0)}分)")
            
            # 三煞信息
            sansha_info = result.get('sansha_info', {})
            if sansha_info:
                sansha_parts = []
                if sansha_info.get('year_sansha_day_fan'):
                    sansha_parts.append('年三煞犯日柱')
                if sansha_info.get('year_sansha_month_fan'):
                    sansha_parts.append('年三煞犯月柱')
                if sansha_info.get('year_sansha_fan'):
                    sansha_parts.append('年三煞犯山向')
                if sansha_info.get('month_sansha_fan'):
                    sansha_parts.append('月三煞犯山向')
                if sansha_parts:
                    lines.append(f"  ⚠️ 犯煞：{'、'.join(sansha_parts)}")
        
        # 建议
        lines.append("")
        lines.append("=" * 80)
        lines.append("使用建议")
        lines.append("=" * 80)
        lines.append("")
        lines.append("1. 优先选择评分130分以上的吉日")
        lines.append("2. 避开犯三煞、冲事主生肖的日期")
        lines.append("3. 结合个人八字五行喜忌选择最合适的日子")
        lines.append("4. 重要事项建议咨询专业择日师")
        lines.append("")
        lines.append("=" * 80)
        lines.append("报告结束")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_html_report(self):
        """生成HTML报告
        
        Returns:
            str: HTML格式的报告
        """
        # 统计信息
        total_count = len(self.results)
        good_count = sum(1 for r in self.results if r.get('score', 0) >= 100)
        excellent_count = sum(1 for r in self.results if r.get('score', 0) >= 130)
        bad_count = sum(1 for r in self.results if r.get('score', 0) < 60)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>专业级正五行择日报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }}
        
        .header .subtitle {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .info-section {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }}
        
        .info-section h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .info-item {{
            display: flex;
            align-items: center;
            padding: 10px 15px;
            background: white;
            border-radius: 8px;
        }}
        
        .info-label {{
            color: #666;
            font-size: 14px;
            margin-right: 10px;
        }}
        
        .info-value {{
            color: #333;
            font-weight: 600;
        }}
        
        .stats-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stat-card.excellent {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.good {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.bad {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .results-section {{
            margin-bottom: 25px;
        }}
        
        .results-section h3 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .result-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }}
        
        .result-card:hover {{
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
            border-color: #667eea;
        }}
        
        .result-card.excellent {{
            border-color: #11998e;
            background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
        }}
        
        .result-card.good {{
            border-color: #f093fb;
        }}
        
        .result-card.bad {{
            border-color: #eb3349;
            opacity: 0.7;
        }}
        
        .result-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .result-rank {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }}
        
        .result-card.excellent .result-rank {{ background: #11998e; }}
        
        .result-date {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        
        .result-score {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .result-card.excellent .result-score {{ color: #11998e; }}
        
        .result-level {{
            font-size: 14px;
            color: #666;
            margin-left: 10px;
        }}
        
        .result-sizhu {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}
        
        .result-sizhu-label {{
            color: #666;
            font-size: 12px;
            margin-bottom: 8px;
        }}
        
        .result-sizhu-value {{
            font-family: "Consolas", "Monaco", monospace;
            font-size: 16px;
            color: #333;
            letter-spacing: 2px;
        }}
        
        .result-sizhu-detail {{
            color: #666;
            font-size: 13px;
            margin-top: 5px;
        }}
        
        .result-yi-ji {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .yi-box, .ji-box {{
            padding: 12px;
            border-radius: 8px;
        }}
        
        .yi-box {{
            background: #d4edda;
            color: #155724;
        }}
        
        .ji-box {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .yi-box h4, .ji-box h4 {{
            font-size: 14px;
            margin-bottom: 8px;
        }}
        
        .yi-list, .ji-list {{
            list-style: none;
            padding: 0;
        }}
        
        .yi-list li, .ji-list li {{
            font-size: 13px;
            padding: 3px 0;
        }}
        
        .shensha-section {{
            margin-top: 15px;
        }}
        
        .shensha-title {{
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .shensha-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 8px;
        }}
        
        .shensha-item {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
        }}
        
        .shensha-item.good {{
            background: #d4edda;
            color: #155724;
        }}
        
        .shensha-item.bad {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .shensha-name {{
            font-weight: 600;
            margin-right: 8px;
        }}
        
        .shensha-score {{
            font-weight: bold;
        }}
        
        .sansha-warning {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 10px 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 14px;
        }}
        
        .advice-section {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-top: 25px;
        }}
        
        .advice-section h3 {{
            margin-bottom: 15px;
            font-size: 20px;
        }}
        
        .advice-list {{
            list-style: none;
            padding: 0;
        }}
        
        .advice-list li {{
            padding: 10px 0;
            font-size: 15px;
            line-height: 1.6;
        }}
        
        .advice-list li::before {{
            content: "💡 ";
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>专业级正五行择日报告</h1>
            <p class="subtitle">生成时间：{self.generate_time}</p>
        </div>
        
        <div class="content">
            <div class="info-section">
                <h3>📋 择日信息</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">事项类型：</span>
                        <span class="info-value">{self.event_type}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">日期范围：</span>
                        <span class="info-value">{self.start_date} 至 {self.end_date}</span>
                    </div>
'''
        
        if self.shan_xiang:
            html += f'''                    <div class="info-item">
                        <span class="info-label">山向：</span>
                        <span class="info-value">{self.shan_xiang}</span>
                    </div>
'''
        
        if self.owners:
            html += '''                </div>
            </div>
            
            <div class="info-section">
                <h3>👥 事主信息</h3>
                <div class="info-grid">
'''
            for owner in self.owners:
                name = owner.get('name', '事主')
                zodiac = owner.get('生肖', '')
                gender = owner.get('性别', '')
                html += f'''                    <div class="info-item">
                        <span class="info-value">{name}（{gender}，{zodiac}）</span>
                    </div>
'''
        
        html += f'''                </div>
            </div>
            
            <div class="stats-section">
                <div class="stat-card">
                    <div class="stat-value">{total_count}</div>
                    <div class="stat-label">总天数</div>
                </div>
                <div class="stat-card excellent">
                    <div class="stat-value">{excellent_count}</div>
                    <div class="stat-label">上吉天数 (≥130分)</div>
                </div>
                <div class="stat-card good">
                    <div class="stat-value">{good_count}</div>
                    <div class="stat-label">吉天数 (≥100分)</div>
                </div>
                <div class="stat-card bad">
                    <div class="stat-value">{bad_count}</div>
                    <div class="stat-label">凶天数 (<60分)</div>
                </div>
            </div>
            
            <div class="results-section">
                <h3>📅 详细择日结果（按评分排序）</h3>
'''
        
        # 添加每个结果
        for i, result in enumerate(self.results, 1):
            score = result.get('score', 0)
            level = result.get('level', '-')
            date_str = result.get('date', '-')
            sizhu = result.get('sizhu', {})
            
            # 确定卡片样式
            card_class = 'result-card'
            if score >= 130:
                card_class += ' excellent'
            elif score >= 100:
                card_class += ' good'
            elif score < 60:
                card_class += ' bad'
            
            html += f'''                <div class="{card_class}">
                    <div class="result-header">
                        <span class="result-rank">第{i}名</span>
                        <span class="result-date">{date_str}</span>
                        <span>
                            <span class="result-score">{score}</span>
                            <span style="font-size:14px;color:#666;">分</span>
                            <span class="result-level">{level}</span>
                        </span>
                    </div>
'''
            
            # 四柱信息
            if isinstance(sizhu, dict):
                html += f'''                    <div class="result-sizhu">
                        <div class="result-sizhu-label">四柱排盘</div>
                        <div class="result-sizhu-value">{sizhu.get('年柱', '')} {sizhu.get('月柱', '')} {sizhu.get('日柱', '')} {sizhu.get('时柱', '')}</div>
                        <div class="result-sizhu-detail">年：{sizhu.get('year_gan', '')}({sizhu.get('year_zhi', '')}) | 月：{sizhu.get('month_gan', '')}({sizhu.get('month_zhi', '')}) | 日：{sizhu.get('day_gan', '')}({sizhu.get('day_zhi', '')}) | 时：{sizhu.get('hour_gan', '')}({sizhu.get('hour_zhi', '')})</div>
                    </div>
'''
            elif isinstance(sizhu, str):
                html += f'''                    <div class="result-sizhu">
                        <div class="result-sizhu-label">四柱</div>
                        <div class="result-sizhu-value">{sizhu}</div>
                    </div>
'''
            
            # 宜忌
            yi_list = result.get('yi_list', [])
            ji_list = result.get('ji_list', [])
            
            html += '                    <div class="result-yi-ji">'
            if yi_list:
                yi_text = '、'.join(yi_list[:5])
                html += f'''                        <div class="yi-box">
                            <h4>✅ 宜</h4>
                            <ul class="yi-list">
                                <li>{yi_text}</li>
                            </ul>
                        </div>
'''
            else:
                html += '''                        <div class="yi-box">
                            <h4>✅ 宜</h4>
                            <ul class="yi-list"><li>无</li></ul>
                        </div>
'''
            
            if ji_list:
                ji_text = '、'.join(ji_list[:3])
                html += f'''                        <div class="ji-box">
                            <h4>❌ 忌</h4>
                            <ul class="ji-list">
                                <li>{ji_text}</li>
                            </ul>
                        </div>
'''
            else:
                html += '''                        <div class="ji-box">
                            <h4>❌ 忌</h4>
                            <ul class="ji-list"><li>无</li></ul>
                        </div>
'''
            html += '                    </div>'
            
            # 神煞
            shensha_list = result.get('shensha_list', [])
            if shensha_list:
                yi_shensha = [s for s in shensha_list if isinstance(s, dict) and s.get('score', 0) > 0]
                ji_shensha = [s for s in shensha_list if isinstance(s, dict) and s.get('score', 0) < 0]
                
                if yi_shensha or ji_shensha:
                    html += '''                    <div class="shensha-section">
                        <div class="shensha-title">神煞详情</div>
                        <div class="shensha-grid">
'''
                    for s in yi_shensha[:4]:
                        html += f'                            <div class="shensha-item good"><span class="shensha-name">{s.get("name", "")}</span><span class="shensha-score">+{s.get("score", 0)}分</span></div>\n'
                    for s in ji_shensha[:4]:
                        html += f'                            <div class="shensha-item bad"><span class="shensha-name">{s.get("name", "")}</span><span class="shensha-score">{s.get("score", 0)}分</span></div>\n'
                    html += '''                        </div>
                    </div>
'''
            
            # 三煞警告
            sansha_info = result.get('sansha_info', {})
            sansha_parts = []
            if sansha_info.get('year_sansha_day_fan'):
                sansha_parts.append('年三煞犯日柱')
            if sansha_info.get('year_sansha_month_fan'):
                sansha_parts.append('年三煞犯月柱')
            if sansha_info.get('year_sansha_fan'):
                sansha_parts.append('年三煞犯山向')
            if sansha_info.get('month_sansha_fan'):
                sansha_parts.append('月三煞犯山向')
            
            if sansha_parts:
                html += f'''                    <div class="sansha-warning">
                        ⚠️ <strong>犯煞警告：</strong>{'、'.join(sansha_parts)}
                    </div>
'''
            
            html += '                </div>'
        
        # 建议
        html += f'''            </div>
            
            <div class="advice-section">
                <h3>💡 使用建议</h3>
                <ul class="advice-list">
                    <li>优先选择评分130分以上的上吉日</li>
                    <li>避开犯三煞、冲事主生肖的日期</li>
                    <li>结合个人八字五行喜忌选择最合适的日子</li>
                    <li>查看宜忌详情，确认与事项匹配</li>
                    <li>重要事项建议咨询专业择日师</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>专业级正五行择日系统 v1.0 | 报告仅供参考</p>
            <p>生成时间：{self.generate_time}</p>
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def save_text(self, filename):
        """保存文本报告
        
        Args:
            filename: 文件名
        """
        content = self.generate_text_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def save_html(self, filename):
        """保存HTML报告
        
        Args:
            filename: 文件名
        """
        content = self.generate_html_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def save_pdf(self, filename):
        """保存PDF报告（需要安装weasyprint或其他PDF库）
        
        Args:
            filename: 文件名
        """
        try:
            # 尝试使用weasyprint
            from weasyprint import HTML
            html_content = self.generate_html_report()
            HTML(string=html_content).write_pdf(filename)
            return True
        except ImportError:
            # 如果没有weasyprint，保存为HTML并提示用户
            html_filename = filename.replace('.pdf', '.html')
            self.save_html(html_filename)
            print(f"PDF导出需要weasyprint库，已保存为HTML文件：{html_filename}")
            print("可使用浏览器打开HTML文件后打印为PDF")
            return False


def generate_report(results, event_type, start_date, end_date, shan_xiang=None, owners=None):
    """生成择日报告
    
    Args:
        results: 择日结果列表
        event_type: 事项类型
        start_date: 开始日期
        end_date: 结束日期
        shan_xiang: 山向
        owners: 事主信息
        
    Returns:
        ReportGenerator: 报告生成器实例
    """
    generator = ReportGenerator(event_type, start_date, end_date, shan_xiang, owners)
    generator.add_results(results)
    return generator


if __name__ == '__main__':
    # 测试代码
    test_results = [
        {
            'date': '2026-10-23',
            'score': 185,
            'level': '★★★★ 大吉',
            'sizhu': {'年柱': '丙午', '月柱': '戊戌', '日柱': '庚午', '时柱': '辛巳',
                      'year_gan': '丙', 'year_zhi': '午', 'month_gan': '戊', 'month_zhi': '戌',
                      'day_gan': '庚', 'day_zhi': '午', 'hour_gan': '辛', 'hour_zhi': '巳'},
            'yi_list': ['建除成日宜入宅', '不将日宜修造', '坤山得午生扶'],
            'ji_list': [],
            'shensha_list': [
                {'name': '天德', 'score': 15, 'description': '天德日，大吉'},
                {'name': '月德', 'score': 12, 'description': '月德日，大吉'}
            ],
            'sansha_info': {}
        }
    ]
    
    generator = generate_report(test_results, '入宅', '2026-10-01', '2026-10-31', '坤山艮向兼未')
    
    # 保存文本报告
    generator.save_text('test_report.txt')
    print("文本报告已保存为 test_report.txt")
    
    # 保存HTML报告
    generator.save_html('test_report.html')
    print("HTML报告已保存为 test_report.html")

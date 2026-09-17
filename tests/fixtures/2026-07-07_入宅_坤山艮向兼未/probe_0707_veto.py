# -*- coding: utf-8 -*-
import sys, datetime
sys.path.insert(0, sys.argv[1])
from modules.四柱计算器 import calculate_sizhu
from modules.评分器 import calculate_score
owners=[{'name':'事主1','sizhu':'辛亥 辛丑 戊戌 丙辰','xishen':'水、木','yongshen':'水'}]
HOURS=[(0,'子'),(2,'丑'),(4,'寅'),(6,'卯'),(8,'辰'),(10,'巳'),(12,'午'),(14,'未'),(16,'申'),(18,'酉'),(20,'戌'),(22,'亥')]
def show(d, event, shan):
    print('==== %s %s %s ===='%(d,event,shan or ''))
    for hh,hz in HOURS:
        sz=calculate_sizhu(d,hh,0); sz['year']=d.year; sz['month']=d.month; sz['day']=d.day; sz['date']=d
        r=calculate_score(sz,event,owners,'',shan,'','','')
        v=r.get('veto_reasons') or []
        print('  %s时 分=%-4s 否=%d  %s'%(hz, r.get('score'), len(v), ' | '.join(str(x) for x in v)))
show(datetime.date(2026,7,7),'入宅','坤山艮向')
show(datetime.date(2026,7,16),'入宅','坤山艮向')

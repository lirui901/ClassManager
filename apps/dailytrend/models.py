from django.db import models
from django.utils import timezone
import random

class DailyTrend(models.Model):
    """每日趋势（宜忌）"""
    date = models.DateField('日期', unique=True)
    suitable_items = models.TextField('宜', help_text='多个事项用逗号分隔')
    unsuitable_items = models.TextField('忌', help_text='多个事项用逗号分隔')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '每日趋势'
        verbose_name_plural = '每日趋势'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} 趋势"
    
    @classmethod
    def get_today_trend(cls):
        """获取今天的趋势，如果不存在则随机生成"""
        today = timezone.now().date()
        trend, created = cls.objects.get_or_create(
            date=today,
            defaults={
                'suitable_items': cls.generate_random_suitable(),
                'unsuitable_items': cls.generate_random_unsuitable()
            }
        )
        return trend
    
    @staticmethod
    def generate_random_suitable():
        """随机生成宜的事项"""
        suitable_list = [
            "学习,读书,思考", "运动,锻炼,健身", "社交,聚会,交流",
            "工作,创作,写作", "冥想,静坐,放松", "旅行,探索,冒险",
            "投资,理财,规划", "沟通,谈判,签约", "创新,突破,尝试",
            "整理,收纳,清洁", "休息,调养,养生", "教学,分享,指导",
            "合作,团队,共赢", "研究,分析,总结", "计划,目标,执行"
        ]
        return random.choice(suitable_list)
    
    @staticmethod
    def generate_random_unsuitable():
        """随机生成忌的事项"""
        unsuitable_list = [
            "熬夜,过度劳累", "冲动消费,投资", "争吵,冲突,固执",
            "懒惰,拖延,放弃", "暴饮暴食,酗酒", "冒险,投机,赌博",
            "批评,指责,抱怨", "急躁,焦虑,紧张", "孤立,自闭,逃避",
            "欺骗,谎言,失信", "攀比,嫉妒,虚荣", "过度娱乐,沉迷",
            "轻信他人,草率决定", "固执己见,不听劝告", "消极,悲观,放弃"
        ]
        return random.choice(unsuitable_list)
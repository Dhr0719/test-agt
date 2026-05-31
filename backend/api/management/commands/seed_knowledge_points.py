from django.core.management.base import BaseCommand
from api.models import KnowledgePoint


class Command(BaseCommand):
    help = "初始化知识点种子数据"

    def handle(self, *args, **options):
        data = [
            {"id": 1, "name": "Python基础语法", "description": "Python 基础语法知识", "category": "Python", "keywords": "变量,数据类型,运算符,控制流"},
            {"id": 2, "name": "函数", "description": "函数的定义与调用", "category": "Python", "keywords": "def,参数,返回值,作用域"},
            {"id": 3, "name": "装饰器", "description": "装饰器的原理与使用", "category": "Python进阶", "keywords": "装饰器,@,闭包,高阶函数"},
            {"id": 4, "name": "面向对象", "description": "面向对象编程基础", "category": "Python进阶", "keywords": "class,继承,多态,封装"},
            {"id": 5, "name": "文件操作", "description": "Python 文件读写操作", "category": "Python", "keywords": "open,read,write,with"},
        ]

        for item in data:
            obj, created = KnowledgePoint.objects.update_or_create(
                id=item["id"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "category": item["category"],
                    "keywords": item["keywords"],
                },
            )
            status = "新建" if created else "更新"
            self.stdout.write(self.style.SUCCESS(f"  [{status}] {obj}"))

        self.stdout.write(self.style.SUCCESS("种子数据初始化完成！"))

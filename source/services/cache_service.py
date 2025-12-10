import redis
import json
import hashlib
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

class CacheService:
    def __init__(self,
                 redis_host='localhost',
                 redis_port=6379,
                 mongo_uri='mongodb://localhost:27017'):
        """
        初始化缓存和数据库服务
        """
        # Redis 缓存配置
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )

        # MongoDB 配置
        self.mongo_client = AsyncIOMotorClient(mongo_uri)
        self.db = self.mongo_client['resume_analysis_db']
        self.resume_collection = self.db['resumes']
        self.match_result_collection = self.db['match_results']

    def generate_cache_key(self, data: Dict[str, Any]) -> str:
        """
        根据数据内容生成唯一哈希key
        :param data: 输入数据
        :return: 哈希字符串
        """
        # 将数据转换为确定性字符串
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    async def cache_resume_analysis(self,
                                    resume_info: Dict[str, Any],
                                    analysis_result: Dict[str, Any],
                                    expire_hours: int = 24) -> None:
        """
        缓存简历分析结果
        :param resume_info: 简历信息
        :param analysis_result: 分析结果
        :param expire_hours: 缓存过期时间
        """

        # 生成缓存key
        cache_key = self.generate_cache_key(resume_info)
        # 存储到 Redis
        self.redis_client.setex(
            f"resume_analysis:{cache_key}",
            timedelta(hours=expire_hours),
            json.dumps(analysis_result)
        )

        # 持久化到 MongoDB
        await self.resume_collection.update_one(
            {'cache_key': cache_key},
            {'$set': {
                'resume_info': resume_info,
                'analysis_result': analysis_result,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=expire_hours)
            }},
            upsert=True
        )

    def get_cached_resume_analysis(self, resume_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取缓存的简历分析结果
        :param resume_info: 简历信息
        :return: 缓存结果或 None
        """
        cache_key = self.generate_cache_key(resume_info)
        # 先从 Redis 获取
        cached_result = self.redis_client.get(f"resume_analysis:{cache_key}")
        if cached_result:
            return json.loads(cached_result)
        return None

    async def cache_resume_match_result(self,resume_info: Dict[str, Any],job_description: Dict[str, Any],match_result: Dict[str, Any],expire_hours: int = 24) -> None:
        """
        缓存简历匹配结果
        :param resume_info: 简历信息
        :param job_description: 职位描述
        :param match_result: 匹配结果
        :param expire_hours: 缓存过期时间
        """

        # 生成缓存key
        cache_key = self.generate_cache_key({
            'resume_info': resume_info,
            'job_description': job_description
        })

        # 存储到 Redis
        self.redis_client.setex(
            f"resume_match:{cache_key}",
            timedelta(hours=expire_hours),
            json.dumps(match_result)
        )

        # 持久化到 MongoDB
        await self.match_result_collection.update_one(
            {'cache_key': cache_key},
            {'$set': {
                'resume_info': resume_info,
                'job_description': job_description,
                'match_result': match_result,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=expire_hours)
            }},
            upsert=True
        )

    def get_cached_resume_match(self,
                                resume_info: Dict[str, Any],
                                job_description: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取缓存的简历匹配结果
        :param resume_info: 简历信息
        :param job_description: 职位描述
        :return: 缓存结果或 None
        """
        cache_key = self.generate_cache_key({
            'resume_info': resume_info,
            'job_description': job_description
        })

        # 先从 Redis 获取
        cached_result = self.redis_client.get(f"resume_match:{cache_key}")
        if cached_result:
            return json.loads(cached_result)
        return None

    async def clear_expired_cache(self):
        """
        清理过期缓存
        """

        # MongoDB 清理过期文档
        await self.resume_collection.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        await self.match_result_collection.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })

# 缓存服务单例
cache_service = CacheService()
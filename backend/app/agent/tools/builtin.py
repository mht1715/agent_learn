from langchain_core.tools import tool


@tool("get_weather")
def get_weather(city: str) -> str:
    """查询指定城市的天气"""
    fake = {"北京": "晴天，18°C", "上海": "雨，6°C"}
    return fake.get(city, f"没有获取到{city}的天气")


@tool("get_order_status")
def get_order_status(order_id: str) -> str:
    """获取订单状态"""
    fake = {"A001": "已发货", "A002": "已退款"}
    return fake.get(order_id, f"没有获取到订单{order_id}")

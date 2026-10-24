import json


def read_model_json(text):
    # модель иногда пишет ```json или текст вокруг ответа, нам нужен сам словарь
    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None

    if type(data) is not dict:
        return None
    return data


def scene_is_ok(data):
    if not data or not data.get("scene"):
        return False
    actions = data.get("actions")
    if type(actions) is not list or len(actions) == 0:
        return False
    return True

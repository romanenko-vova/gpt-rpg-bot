import json


def read_model_json(text):
    # Модель иногда дописывает пояснения вокруг JSON. Берём текст внутри скобок.
    if not isinstance(text, str):
        return None

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end < start:
        return None

    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def is_valid_scene(scene, require_three_actions=True):
    # Для новой сцены ждём три действия. В старых сохранениях их могло быть меньше.
    if not isinstance(scene, dict):
        return False

    description = scene.get("scene")
    if not isinstance(description, str) or not description:
        return False

    actions = scene.get("actions")
    if not isinstance(actions, list) or not actions:
        return False
    if require_three_actions and len(actions) != 3:
        return False

    for action in actions:
        if not isinstance(action, str):
            return False
    return True

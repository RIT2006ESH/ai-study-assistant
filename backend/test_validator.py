from app.services.query_validator import get_validator

try:
    validator = get_validator(use_ai_validation=True, strict_mode=False)
    result = validator.process_query("Help me solve quadratic equations")
    print("Result:", result)
except Exception as e:
    print("ERROR:", e)
    import traceback
    traceback.print_exc()

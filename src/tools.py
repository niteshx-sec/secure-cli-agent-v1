# src/tools.py
from pydantic import ValidationError
from src.schemas import CalculatorSchema, SecurityLookupSchema, HashCheckSchema

# 1. Pure Tool Functions
def calc_tool(op: str, val1: int, val2: int) -> str:
    if op == "add":
        return str(val1 + val2)
    elif op == "multiply":
        return str(val1 * val2)
    return "ERROR"

def cve_lookup_tool(cve_id: str, include_mitigation: bool = True) -> str:
    # Deterministic threat intelligence mock
    threat_db = {
        "CVE-2024-3094": "CRITICAL (CVSS 10.0) - XZ Utils Backdoor. Mitigation: Downgrade to 5.4.",
        "CVE-2021-44228": "CRITICAL (CVSS 10.0) - Log4Shell RCE. Mitigation: Patch log4j-core."
    }
    return threat_db.get(cve_id, f"CVE {cve_id} found: SEVERITY UNKNOWN. Monitor endpoint.")


# 2. Tool Dispatcher
class AgentToolDispatcher:
    def __init__(self):
        self.registry = {}

    def register(self, name: str, description: str, schema, func) -> None:
        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": schema.model_json_schema()
            }
        }
        self.registry[name] = {"schema": schema, "func": func, "definition": tool_def}

    def dispatch(self, tool_name: str, raw_arguments: dict) -> str:
        if tool_name not in self.registry:
            return "ERROR: Tool not found."
        
        target = self.registry[tool_name]
        try:
            validated_args = target["schema"](**raw_arguments)
            return target["func"](**validated_args.model_dump())
        except ValidationError as err:
            return f"VALIDATION_BLOCKED: {err}"
        except Exception as runtime_err:
            return f"RUNTIME_ERROR: {runtime_err}"

    def get_definitions(self) -> list:
        return [tool["definition"] for tool in self.registry.values()]
def hash_check_tool(file_Hash: str, algorithm: str) -> str:
    return f"HASH_AUDIT [{algorithm.upper()}]: Safe. Zero malicious signatures matched."
    
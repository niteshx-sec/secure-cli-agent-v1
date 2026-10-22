# main.py
import sys
from src.agent import SecureReActAgent
from src.schemas import CalculatorSchema, SecurityLookupSchema
from src.tools import calc_tool, cve_lookup_tool
from src.schemas import CalculatorSchema, SecurityLookupSchema, HashCheckSchema
from src.tools import calc_tool, cve_lookup_tool, hash_check_tool
def bootstrap_agent() -> SecureReActAgent:
    agent = SecureReActAgent(max_steps=4)
    # Register production tools
    agent.dispatcher.register(
        name="calculator",
        description="Perform arithmetic operations (add, multiply).",
        schema=CalculatorSchema,
        func=calc_tool
    )
    agent.dispatcher.register(
        name="cve_lookup",
        description="Lookup threat intelligence for CVE IDs (format: CVE-YYYY-NNNN).",
        schema=SecurityLookupSchema,
        func=cve_lookup_tool
    )
    agent.dispatcher.register(
        name="hash_checker",
        schema=HashCheckSchema,
        func=hash_check_tool,
        description="Analyzes MD5 or SHA256 file hashes to check for known malicious signatures."
    )
    return agent
    

def main():
    print("=" * 65)
    print("  SECURE CLI AGENT v1.0 [PRODUCTION AUTONOMOUS ENGINE]")
    print("  Active Guardrails: Pydantic Validation | ReAct Loop | Circuit Breakers")
    print("=" * 65)
    print("Type your query below. Type 'exit' or 'quit' to terminate.\n")

    agent = bootstrap_agent()

    while True:
        try:
            user_input = input("\n[USER] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Shutting down agent session. Goodbye.")
                break

            print("[AGENT] Thinking and evaluating tools...")
            result = agent.run(user_input)

            if result["circuit_broken"]:
                print(f"[SECURITY ALERT] {result['answer']}")
            else:
                print(f"[RESPONSE] ({result['steps']} steps taken):")
                print(result["answer"])

        except KeyboardInterrupt:
            print("\nForce shutdown detected. Exiting.")
            sys.exit(0)
        except Exception as e:
            print(f"[SYSTEM ERROR] {e}")

if __name__ == "__main__":
    main()
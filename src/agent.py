# src/agent.py
import os
import json
from dotenv import load_dotenv
from groq import Groq
from src.tools import AgentToolDispatcher

load_dotenv()

class SecureReActAgent:
    def __init__(self, model_name: str = "openai/gpt-oss-20b", max_steps: int = 4):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("CRITICAL: GROQ_API_KEY is not set in environment!")
        
        self.client = Groq(api_key=api_key)
        self.model = model_name
        self.max_steps = max_steps
        self.dispatcher = AgentToolDispatcher()
        self.messages = []

    def run(self, user_prompt: str) -> dict:
        self.messages = [
            {"role": "system", "content": "You are a secure, autonomous AI Agent. Reason step by step and call tools when needed."}
        ]
        self.messages.append({"role": "user", "content": user_prompt})
        tools = self.dispatcher.get_definitions()
        
        step = 0
        while step < self.max_steps:
            step += 1
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools if tools else None,
                tool_choice="auto"
            )
            msg = response.choices[0].message

            # Final response check (No tool called)
            if not msg.tool_calls:
                self.messages.append({"role": "assistant", "content": msg.content})
                return {
                    "answer": msg.content,
                    "steps": step,
                    "circuit_broken": False
                }

            # Tool Execution Protocol
            self.messages.append(msg)
            for call in msg.tool_calls:
                fn_name = call.function.name
                call_id = call.id
                raw_args = json.loads(call.function.arguments)
                
                # Execute via Pydantic-validated dispatcher
                execution_result = self.dispatcher.dispatch(fn_name, raw_args)
                
                # Append mandatory tool response
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": fn_name,
                    "content": str(execution_result)
                })

        return {
            "answer": "EXECUTION_ABORTED: Circuit breaker tripped due to excessive steps.",
            "steps": step,
            "circuit_broken": True
        }
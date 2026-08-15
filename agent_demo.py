import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from weather_agent import root_agent


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent)
    session_id = "terminale"
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="user",
        session_id=session_id,
    )

    print("Premi Ctrl+C per terminare.")
    try:
        while True:
            prompt = input("\nTu: ").strip()
            if not prompt:
                continue
            message = types.Content(role="user", parts=[types.Part(text=prompt)])
            async for event in runner.run_async(
                user_id="user", session_id=session_id, new_message=message
            ):
                if event.is_final_response() and event.content:
                    print("Agente:", event.content.parts[0].text)
    except (KeyboardInterrupt, EOFError):
        print("\nChiusura...")


if __name__ == "__main__":
    asyncio.run(main())

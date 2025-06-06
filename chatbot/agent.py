import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Union
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_ollama import OllamaLLM
import io
import base64


def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()


def create_agent_for_dataframe_sheets(sheets_dfs: dict, question: Optional[str] = None) -> Union[dict, str]:
    combined_df = None
    for sheet, df,_ in sheets_dfs:
        df = df.copy()
        df["sheet_name"] = sheet
        combined_df = pd.concat([combined_df, df], ignore_index=True) if combined_df is not None else df

    llm = OllamaLLM(model="llama3:8b")
    agent = create_pandas_dataframe_agent(
        llm=llm,
        df=combined_df,
        verbose=False,
        allow_dangerous_code=True
    )

    if question:
        response = agent.invoke({"input": f"Only return the final answer. Do not explain. {question}"})
        output = response.get("output", "No output found")

        # Try generating plot if requested
        if any(x in question.lower() for x in ["plot", "chart", "graph", "visualize"]):
            try:
                # You can customize this based on your domain
                fig, ax = plt.subplots()
                combined_df.plot(ax=ax)  # Customize this depending on the user query
                plot_base64 = plot_to_base64(fig)
                return {
                    "output": output,
                    "plot_base64": plot_base64
                }
            except Exception as e:
                return {
                    "output": output,
                    "plot_error": str(e)
                }

        return output

    return agent


def rephrase_prompts(prompts: list[str], max_prompts: int = 10) -> list[str]:
    conversational_prompts = []
    llm = OllamaLLM(model="llama3:8b")

    for prompt in prompts[:max_prompts]:
        llm_input = (
           f"Rephrase the following analytical question to be more natural and conversational for a user interface. "
            f"Keep it friendly and precise:\n\n"
            f"{prompt}"
        )
        try:
            refined = llm(llm_input).strip()
            conversational_prompts.append(refined)
        except Exception as e:
            conversational_prompts.append(prompt)  # fallback

    return conversational_prompts
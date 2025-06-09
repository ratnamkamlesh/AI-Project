import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Union
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_ollama import OllamaLLM
import io
import base64
import os


def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()


def create_agent_for_dataframe_sheets(sheets_dfs: dict, question: Optional[str] = None) -> Union[dict, str]:
    combined_df = None
    for sheet, df,_ in sheets_dfs:
        df = df.copy()
        # Add sheet_name first before any column filtering
        df["sheet_name"] = sheet
        
        # Only keep necessary columns to reduce memory usage
        if question:
            relevant_cols = [col for col in df.columns if any(term in question.lower() for term in col.lower().split('_'))]
            if relevant_cols and 'sheet_name' not in relevant_cols:
                relevant_cols.append('sheet_name')  # Ensure sheet_name is included
            if relevant_cols:
                df = df[relevant_cols]
        
        combined_df = pd.concat([combined_df, df], ignore_index=True) if combined_df is not None else df

    # Optimize DataFrame memory usage
    for col in combined_df.columns:
        if combined_df[col].dtype == 'object':
            if combined_df[col].nunique() / len(combined_df) < 0.5:  # If less than 50% unique values
                combined_df[col] = combined_df[col].astype('category')

    llm = OllamaLLM(
        model="mistral:7b",
        temperature=0.1,
        top_k=5,  # Reduced for faster responses
        top_p=0.3,  # Reduced for more focused responses
        num_ctx=512,  # Reduced context window
        repeat_penalty=1.1,
        num_thread=4,  # Use multiple threads
        format="json"
    )
    
    # Create the agent with optimized configuration
    agent = create_pandas_dataframe_agent(
        llm=llm,
        df=combined_df,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=1,  # Single iteration for faster responses
        max_execution_time=30,  # Set maximum execution time
        allow_python_repl=True,
        allow_dangerous_code=True
    )

    if question:
        try:
            # Check if this is a filtering question
            is_filtering_question = any(term in question.lower() for term in ['list', 'show', 'find', 'filter', 'where', 'which'])
            
            if is_filtering_question:
                # Direct DataFrame manipulation for filtering operations
                try:
                    if 'company_type' in combined_df.columns and 'private' in question.lower():
                        filtered_df = combined_df[combined_df['company_type'].str.lower() == 'private']
                        total_count = len(filtered_df)
                        result_list = filtered_df['company_name'].tolist() if 'company_name' in filtered_df.columns else filtered_df.index.tolist()
                        
                        response_text = f"Total private companies found: {total_count}\n\n"
                        response_text += "Companies:\n"
                        for idx, company in enumerate(result_list, 1):
                            response_text += f"{idx}. {company}\n"
                        
                        return response_text
                except Exception as e:
                    print(f"Direct filtering failed: {str(e)}")
                    # Fall back to LLM approach
            
            # Enhanced prompt for better response structure
            structured_prompt = (
                "Follow these instructions carefully:\n"
                "1. If filtering data, show ALL matching records, not just a few\n"
                "2. Always include the total count of matching records\n"
                "3. Format the output as a numbered list\n"
                "4. Include all relevant columns in the output\n"
                "Question: " + question + "\n"
                "Note: If the result contains multiple records, show ALL of them, not just a sample."
            )
            
            response = agent.invoke(
                {"input": structured_prompt},
                handle_parsing_errors=True,
                config={"max_tokens": 2000}  # Increased token limit for longer responses
            )
            
            output = response.get("output", "No output found")
            
            # Process and structure the output
            if isinstance(output, str):
                output = output.replace('```', '').replace('`', '').strip()
                
                # Handle JSON responses
                if output.startswith('{') or output.startswith('['):
                    try:
                        import ast
                        import json
                        
                        # Try both ast.literal_eval and json.loads
                        try:
                            evaluated_output = ast.literal_eval(output)
                        except:
                            evaluated_output = json.loads(output)
                            
                        if isinstance(evaluated_output, dict):
                            if 'answer' in evaluated_output and isinstance(evaluated_output['answer'], list):
                                items = evaluated_output['answer']
                                total_count = len(items)
                                formatted_output = f"Total items found: {total_count}\n\n"
                                for idx, item in enumerate(items, 1):
                                    formatted_output += f"{idx}. {item}\n"
                                output = formatted_output
                            else:
                                output = "\n".join([f"{k}: {v}" for k, v in evaluated_output.items()])
                        elif isinstance(evaluated_output, list):
                            total_count = len(evaluated_output)
                            formatted_output = f"Total items found: {total_count}\n\n"
                            for idx, item in enumerate(evaluated_output, 1):
                                formatted_output += f"{idx}. {item}\n"
                            output = formatted_output
                    except Exception as e:
                        print(f"Error processing structured output: {str(e)}")

            return output
            
        except Exception as e:
            error_msg = str(e)
            if "parsing" in error_msg.lower():
                if "Could not parse LLM output:" in error_msg:
                    start_idx = error_msg.find("Could not parse LLM output:") + len("Could not parse LLM output:")
                    end_idx = error_msg.find("For troubleshooting")
                    if end_idx == -1:
                        end_idx = None
                    actual_response = error_msg[start_idx:end_idx].strip()
                    return actual_response
            return f"Error processing your request: {error_msg}. Please try rephrasing your question."

    return agent


def rephrase_prompts(prompts: list[str], max_prompts: int = 10) -> list[str]:
    """
    Rephrase the given prompts using Ollama LLM
    """
    conversational_prompts = []
    llm = OllamaLLM(
        model="mistral:7b",
        temperature=0.1,
        top_k=5,
        top_p=0.3,
        num_ctx=512,
        repeat_penalty=1.1,
        num_thread=4,
        format="json"
    )

    for prompt in prompts[:max_prompts]:
        try:
            llm_input = (
                "Rephrase the following question to make it more conversational and clear. "
                "Keep it concise and natural: " + prompt
            )
            refined = llm(llm_input).strip()
            # Clean up any JSON or code formatting
            refined = refined.replace('```', '').replace('`', '').strip()
            if refined.startswith('{') or refined.startswith('['):
                try:
                    import ast
                    evaluated = ast.literal_eval(refined)
                    if isinstance(evaluated, dict) and 'response' in evaluated:
                        refined = evaluated['response']
                    elif isinstance(evaluated, str):
                        refined = evaluated
                except:
                    pass
            conversational_prompts.append(refined)
        except Exception as e:
            print(f"Error rephrasing prompt: {str(e)}")
            conversational_prompts.append(prompt)  # fallback to original prompt

    return conversational_prompts
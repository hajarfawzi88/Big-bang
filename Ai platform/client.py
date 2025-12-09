from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import asyncio
import logging
import json
from LLM import generate_content_sync


logging.basicConfig(
    filename='client.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
prompt="""You are an AI assistant integrated into a Model Context Protocol (MCP) system. 
    You have access to the following tools:

    {tools_list}

    Each tool has a name, description, and parameters (input schema). Your task is to:
    1. Read the user's input describing what they want to achieve.
    2. Determine the best tool(s) from the list that can be used to accomplish their task.
    3. For each selected tool, extract or infer the required arguments from the user's request based on the tool's parameters.
    4. If multiple tools are required in sequence, list them in order and describe how they will work together.
    5. If no tools match the user's description, reply with an empty selected_tools array.

    IMPORTANT: For each tool, you MUST provide the correct arguments based on the tool's parameters schema. 
    Extract argument values from the user's request. If a required argument is not provided in the user request, 
    use reasonable defaults or infer from context.

    Respond in JSON format as follows:

    {{
    "selected_tools": [
        {{
            "tool_name": "tool_name_1",
            "arguments": {{"arg1": "value1", "arg2": "value2"}}
        }},
        {{
            "tool_name": "tool_name_2",
            "arguments": {{"arg1": "value1"}}
        }}
    ],
    "explanation": "Brief explanation why these tools are selected and how they can solve the user's task."
    }}

    Here is the user request:
    "{user_request}"
    """



async def main():
    async with streamablehttp_client("http://localhost:8000/mcp") as (reader, writer, session_id):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            logging.info("Connected to MCP server")

            # List tools
            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            print("Available tool names:", tool_names)
            logging.info(f"Available tool names: {tool_names}")
            
            # Format tools list for LLM prompt with schema information
            tools_description = "\n".join([
                f"- {tool.name}: {tool.description}\n  Parameters: {getattr(tool, 'inputSchema', getattr(tool, 'input_schema', 'No parameters'))}" 
                for tool in tools.tools
            ]) if tools.tools else "No tools available"
            
            # Create a mapping of tool names to tool definitions for easy lookup
            tools_map = {tool.name: tool for tool in tools.tools}
            
            print("Available tools:", tools_description)
            logging.info(f"Available tools: {tools_description}")
            
            # Example user request - you can modify this or make it interactive
            user_request = input("What is on your mind?")
            
            # Use LLM to select appropriate tools
            formatted_prompt = prompt.format(
                tools_list=tools_description,
                user_request=user_request
            )
            
            print("\nUsing LLM to select tools...")
            logging.info("Using LLM to select tools based on user request")
            
            try:
                llm_response = generate_content_sync(formatted_prompt)
                print("LLM Response:", llm_response)
                logging.info(f"LLM Response: {llm_response}")
                
                # Try to parse JSON response
                try:
                    # Extract JSON from response (in case LLM adds extra text)
                    json_start = llm_response.find('{')
                    json_end = llm_response.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        json_str = llm_response[json_start:json_end]
                        tool_selection = json.loads(json_str)
                        
                        selected_tools = tool_selection.get("selected_tools", [])
                        explanation = tool_selection.get("explanation", "")
                        
                        print(f"\nSelected tools: {selected_tools}")
                        print(f"Explanation: {explanation}")
                        logging.info(f"Selected tools: {selected_tools}, Explanation: {explanation}")
                        
                        # Call the selected tools generically
                        for tool_info in selected_tools:
                            # Handle both old format (string) and new format (dict with tool_name and arguments)
                            if isinstance(tool_info, str):
                                tool_name = tool_info
                                arguments = {}
                            elif isinstance(tool_info, dict):
                                tool_name = tool_info.get("tool_name", tool_info.get("name", ""))
                                arguments = tool_info.get("arguments", {})
                            else:
                                print(f"Warning: Invalid tool format: {tool_info}")
                                logging.warning(f"Invalid tool format: {tool_info}")
                                continue
                            
                            if tool_name in tool_names:
                                print(f"\nCalling tool: {tool_name}")
                                if arguments:
                                    print(f"  Arguments: {arguments}")
                                logging.info(f"Calling tool: {tool_name} with arguments: {arguments}")
                                
                                try:
                                    response = await session.call_tool(tool_name, arguments=arguments)
                                    
                                    # Handle response generically
                                    if response.content:
                                        response_text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
                                        print(f"Response: {response_text}")
                                        logging.info(f"Tool {tool_name} response: {response_text}")
                                    else:
                                        print(f"Response: {response}")
                                        logging.info(f"Tool {tool_name} response: {response}")
                                except Exception as e:
                                    error_msg = f"Error calling tool {tool_name}: {str(e)}"
                                    print(f"Error: {error_msg}")
                                    logging.error(error_msg)
                            else:
                                print(f"Warning: Tool '{tool_name}' not found in available tools")
                                logging.warning(f"Tool '{tool_name}' not found")
                    else:
                        print("Could not parse JSON from LLM response")
                        logging.warning("Could not parse JSON from LLM response")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    logging.error(f"JSON parsing error: {e}")
                    
            except Exception as e:
                print(f"Error using LLM: {e}")
                logging.error(f"LLM error: {e}")
                # Fallback: try to use the first available tool if any
                if tools.tools:
                    print("Falling back to first available tool...")
                    first_tool = tools.tools[0]
                    try:
                        # Try calling with empty arguments (some tools might not need args)
                        response = await session.call_tool(first_tool.name, arguments={})
                        if response.content:
                            response_text = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
                            print(f"Fallback response: {response_text}")
                            logging.info(f"Fallback response: {response_text}")
                    except Exception as fallback_error:
                        print(f"Fallback tool call also failed: {fallback_error}")
                        logging.error(f"Fallback tool call error: {fallback_error}")
                else:
                    print("No tools available for fallback")
                    logging.warning("No tools available for fallback")


if __name__ == "__main__":
    asyncio.run(main())

import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

# --- Vietnam Traffic Law Database ---
TRAFFIC_LAW_DATABASE = """[ĐIỀU 5 - Ô TÔ VI PHẠM NỒNG ĐỘ CỒN]
- Điểm c Khoản 6 Điều 5: Điều khiển xe ô tô trên đường mà nồng độ cồn chưa vượt quá 50 mg/100 ml máu hoặc chưa vượt quá 0.25 mg/l khí thở. Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 10 tháng đến 12 tháng. Tạm giữ xe đến 7 ngày.
- Điểm c Khoản 7 Điều 5: Điều khiển xe ô tô trên đường mà nồng độ cồn vượt quá 50 mg đến 80 mg/100 ml máu hoặc vượt quá 0.25 mg đến 0.4 mg/l khí thở. Phạt tiền từ 16.000.000 đồng đến 18.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 16 tháng đến 18 tháng. Tạm giữ xe đến 7 ngày.
- Điểm a Khoản 8 Điều 5: Điều khiển xe ô tô trên đường mà nồng độ cồn vượt quá 80 mg/100 ml máu hoặc vượt quá 0.4 mg/l khí thở. Phạt tiền từ 30.000.000 đồng đến 40.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 22 tháng đến 24 tháng. Tạm giữ xe đến 7 ngày.

[ĐIỀU 6 - XE MÁY VI PHẠM NỒNG ĐỘ CỒN]
- Điểm c Khoản 6 Điều 6: Điều khiển xe mô tô, xe máy trên đường mà nồng độ cồn chưa vượt quá 50 mg/100 ml máu hoặc chưa vượt quá 0.25 mg/l khí thở. Phạt tiền từ 2.000.000 đồng đến 3.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 10 tháng đến 12 tháng. Tạm giữ xe đến 7 ngày.
- Điểm c Khoản 7 Điều 6: Điều khiển xe mô tô, xe máy trên đường mà nồng độ cồn vượt quá 50 mg đến 80 mg/100 ml máu hoặc vượt quá 0.25 mg đến 0.4 mg/l khí thở. Phạt tiền từ 4.000.000 đồng đến 5.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 16 tháng đến 18 tháng. Tạm giữ xe đến 7 ngày.
- Điểm e Khoản 8 Điều 6: Điều khiển xe mô tô, xe máy trên đường mà nồng độ cồn vượt quá 80 mg/100 ml máu hoặc vượt quá 0.4 mg/l khí thở. Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 22 tháng đến 24 tháng. Tạm giữ xe đến 7 ngày.

[ĐIỀU 5 - Ô TÔ CHẠY QUÁ TỐC ĐỘ]
- Điểm a Khoản 3 Điều 5: Điều khiển xe ô tô chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h. Phạt tiền từ 800.000 đồng đến 1.000.000 đồng.
- Điểm i Khoản 5 Điều 5: Điều khiển xe ô tô chạy quá tốc độ quy định từ 10 km/h đến 20 km/h. Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 01 tháng đến 03 tháng.
- Điểm a Khoản 6 Điều 5: Điều khiển xe ô tô chạy quá tốc độ quy định trên 20 km/h đến 35 km/h. Phạt tiền từ 6.000.000 đồng đến 8.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 02 tháng đến 04 tháng.
- Điểm c Khoản 8 Điều 5: Điều khiển xe ô tô chạy quá tốc độ quy định trên 35 km/h. Phạt tiền từ 10.000.000 đồng đến 12.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 02 tháng đến 04 tháng.

[ĐIỀU 6 - XE MÁY CHẠY QUÁ TỐC ĐỘ]
- Điểm c Khoản 2 Điều 6: Điều khiển xe mô tô, xe máy chạy quá tốc độ quy định từ 05 km/h đến dưới 10 km/h. Phạt tiền từ 300.000 đồng đến 400.000 đồng.
- Điểm a Khoản 4 Điều 6: Điều khiển xe mô tô, xe máy chạy quá tốc độ quy định từ 10 km/h đến 20 km/h. Phạt tiền từ 800.000 đồng đến 1.000.000 đồng.
- Điểm a Khoản 7 Điều 6: Điều khiển xe mô tô, xe máy chạy quá tốc độ quy định trên 20 km/h. Phạt tiền từ 4.000.000 đồng đến 5.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 02 tháng đến 04 tháng.

[ĐIỀU 5 - Ô TÔ VƯỢT ĐÈN ĐỎ, ĐÈN VÀNG]
- Nghị định 100/2019/NĐ-CP (sửa đổi bởi Nghị định 123/2021/NĐ-CP): Không chấp hành hiệu lệnh của đèn tín hiệu giao thông (vượt đèn đỏ, đèn vàng). Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 01 tháng đến 03 tháng (nếu gây tai nạn thì tước GPLX từ 02 tháng đến 04 tháng).
- Nghị định 168/2024/NĐ-CP (áp dụng từ 01/01/2025): Không chấp hành hiệu lệnh của đèn tín hiệu giao thông (vượt đèn đỏ, đèn vàng). Phạt tiền từ 18.000.000 đồng đến 20.000.000 đồng (nếu gây tai nạn phạt từ 20.000.000 đồng đến 22.000.000 đồng). Bị trừ 04 điểm Giấy phép lái xe (nếu gây tai nạn bị trừ 10 điểm).

[ĐIỀU 6 - XE MÁY VƯỢT ĐÈN ĐỎ, ĐÈN VÀNG]
- Nghị định 100/2019/NĐ-CP (sửa đổi bởi Nghị định 123/2021/NĐ-CP): Không chấp hành hiệu lệnh của đèn tín hiệu giao thông (vượt đèn đỏ, đèn vàng). Phạt tiền từ 800.000 đồng đến 1.000.000 đồng. Tước quyền sử dụng Giấy phép lái xe (GPLX) từ 01 tháng đến 03 tháng (nếu gây tai nạn thì tước GPLX từ 02 tháng đến 04 tháng).
- Nghị định 168/2024/NĐ-CP (áp dụng từ 01/01/2025): Không chấp hành hiệu lệnh của đèn tín hiệu giao thông (vượt đèn đỏ, đèn vàng). Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng (nếu gây tai nạn phạt từ 10.000.000 đồng đến 14.000.000 đồng). Bị trừ 04 điểm Giấy phép lái xe (nếu gây tai nạn bị trừ 10 điểm).

[ĐIỀU 5 - Ô TÔ ĐI NGƯỢC CHIỀU]
- Nghị định 100/2019/NĐ-CP (sửa đổi bởi Nghị định 123/2021/NĐ-CP): Đi ngược chiều của đường một chiều, đi ngược chiều trên đường có biển “Cấm đi ngược chiều”. Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng. Tước Giấy phép lái xe (GPLX) từ 02 tháng đến 04 tháng. Nếu đi ngược chiều trên đường cao tốc phạt từ 16.000.000 đồng đến 18.000.000 đồng, tước GPLX từ 05 tháng đến 07 tháng.
- Nghị định 168/2024/NĐ-CP (áp dụng từ 01/01/2025): Đi ngược chiều của đường một chiều, đi ngược chiều trên đường có biển “Cấm đi ngược chiều”. Phạt tiền từ 18.000.000 đồng đến 20.000.000 đồng, bị trừ 04 điểm Giấy phép lái xe (nếu gây tai nạn phạt từ 20.000.000 đồng đến 22.000.000 đồng, bị trừ 10 điểm). Nếu đi ngược chiều trên đường cao tốc phạt từ 30.000.000 đồng đến 40.000.000 đồng, bị trừ 10 điểm Giấy phép lái xe.

[ĐIỀU 6 - XE MÁY ĐI NGƯỢC CHIỀU]
- Nghị định 100/2019/NĐ-CP (sửa đổi bởi Nghị định 123/2021/NĐ-CP): Đi ngược chiều của đường một chiều, đi ngược chiều trên đường có biển “Cấm đi ngược chiều”. Phạt tiền từ 1.000.000 đồng đến 2.000.000 đồng. Tước Giấy phép lái xe (GPLX) từ 01 tháng đến 03 tháng (nếu gây tai nạn phạt từ 4.000.000 đồng đến 5.000.000 đồng, tước GPLX từ 02 đến 04 tháng).
- Nghị định 168/2024/NĐ-CP (áp dụng từ 01/01/2025): Đi ngược chiều của đường một chiều, đi ngược chiều trên đường có biển “Cấm đi ngược chiều”. Phạt tiền từ 4.000.000 đồng đến 6.000.000 đồng, bị trừ 02 điểm Giấy phép lái xe (nếu gây tai nạn phạt từ 10.000.000 đồng đến 14.000.000 đồng, bị trừ 10 điểm).
"""

# --- Traffic Law Tools ---
def search_traffic_law(keywords: str) -> str:
    """
    Search the Vietnam Traffic Law text database for relevant clauses.
    Args:
        keywords (str): The search terms/keywords (e.g., 'xe máy nồng độ cồn', 'ô tô quá tốc độ').
    Returns:
        str: The matching legal clauses found in the database.
    """
    if not isinstance(keywords, str) or not keywords.strip():
        return "Error: Please provide non-empty search keywords."
    
    # Simple self-healing for vehicle slang
    kw_clean = keywords.lower()
    if "xe hơi" in kw_clean or "xe bốn bánh" in kw_clean:
        keywords += " ô tô"
    if "mô tô" in kw_clean or "xe gắn máy" in kw_clean:
        keywords += " xe máy"

    # Split database into sections or paragraphs
    sections = TRAFFIC_LAW_DATABASE.strip().split("\n\n")
    matching_paragraphs = []

    # Split input keywords into individual words for search matching
    search_words = [w.strip() for w in keywords.lower().split() if len(w.strip()) > 1]
    if not search_words:
        search_words = [keywords.lower().strip()]

    for section in sections:
        # Check if the section contains the search terms
        section_lower = section.lower()
        # Count how many search words match in this section
        matches = sum(1 for word in search_words if word in section_lower)
        if matches > 0:
            matching_paragraphs.append((section, matches))

    # Sort matching paragraphs by relevance score (number of matching words)
    matching_paragraphs.sort(key=lambda x: x[1], reverse=True)

    if not matching_paragraphs:
        return f"No direct legal clauses found matching keywords: '{keywords}'."

    # Return top 2 matching sections
    top_matches = [item[0] for item in matching_paragraphs[:2]]
    return "\n\n".join(top_matches)

def calculate_over_speed(actual_speed: str, limit_speed: str) -> float:
    """
    Safely calculate speed overrun (actual_speed - limit_speed) with parameter self-healing.
    Args:
        actual_speed (str/float): Actual speed of the vehicle (e.g. '65 km/h' or 65.0).
        limit_speed (str/float): Speed limit of the road segment (e.g. '50 km/h' or 50.0).
    Returns:
        float: The calculated overrun amount in km/h.
    """
    # Self-healing helper to extract float from string
    def _parse_to_float(val) -> float:
        if isinstance(val, (int, float)):
            return float(val)
        # Regex to extract numeric part
        match = re.search(r"([0-9.]+)", str(val))
        if match:
            return float(match.group(1))
        return 0.0

    act = _parse_to_float(actual_speed)
    lim = _parse_to_float(limit_speed)
    return round(act - lim, 2)


# --- Simple Chatbot Baseline ---
class SimpleChatbot:
    """
    A simple direct LLM chatbot that acts as a baseline comparison to the ReAct agent.
    """
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    def run(self, user_input: str) -> str:
        logger.log_event("CHATBOT_START", {"input": user_input, "model": self.llm.model_name})
        system_prompt = "You are a helpful assistant. Answer the user's traffic violation queries as best as you can."
        
        res = self.llm.generate(user_input, system_prompt=system_prompt)
        
        tracker.track_request(
            provider=res.get("provider", "unknown"),
            model=self.llm.model_name,
            usage=res.get("usage", {}),
            latency_ms=res.get("latency_ms", 0)
        )
        
        content = res.get("content", "").strip()
        logger.log_event("CHATBOT_END", {"response": content})
        return content


# --- ReAct Agent ---
class ReActAgent:
    """
    A ReAct-style Agent that follows the Thought-Action-Observation loop.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""You are a professional assistant specializing in Vietnam Traffic Law (Decree 100/2019/ND-CP and Decree 123/2021/ND-CP).
You have access to the following tools to retrieve accurate legal clauses and perform calculations:
{tool_descriptions}

You must help the driver by following a strict Thought-Action-Observation loop to resolve their query.
To guarantee 100% accuracy and prevent hallucination, DO NOT make up fine amounts or suspension periods. You MUST query the law database using the search tool first to retrieve the exact clause, and then verify the driver's values against the legal rules.

Use the following exact format for each step:
Thought: your line of reasoning about what you need to search or calculate next.
Action: tool_name(parameter_name=parameter_value)
Observation: the result of the tool call.

Note:
- You must output exactly one 'Thought:' and one 'Action:' per step.
- Do not invent/hallucinate tool names. Only use the tools listed above.
- Always specify parameters using keyword syntax, e.g. search_traffic_law(keywords="nồng độ cồn xe máy").
- Once you write 'Action: ...', stop generating and wait for the Observation.

When you have retrieved the exact clauses and verified the driver's violations, output your final response in this exact format:
Thought: I have retrieved the exact legal clauses and verified the violation. I can now answer the user.
Final Answer: your final detailed response to the driver, including the exact fine range, Giấy phép lái xe (GPLX) suspension time, and vehicle impoundment period, citing the exact Article/Clause of the Decree.
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        # 1. ADAPTIVE HYBRID ROUTER
        legal_keywords = ["cồn", "tốc độ", "phạt", "gplx", "bằng lái", "đèn đỏ", "đèn vàng", "thổi", "km/h", "vượt", "xe", "nồng độ", "chạy quá", "ngược chiều", "ngược"]
        if not any(kw in user_input.lower() for kw in legal_keywords):
            logger.log_event("AGENT_ROUTE_DIRECT", {"input": user_input})
            res = self.llm.generate(user_input, system_prompt="You are a polite assistant. Answer directly and concisely.")
            tracker.track_request(
                provider=res.get("provider", "unknown"),
                model=self.llm.model_name,
                usage=res.get("usage", {}),
                latency_ms=res.get("latency_ms", 0)
            )
            content = res.get("content", "").strip()
            logger.log_event("AGENT_END", {"steps": 1})
            return content

        # 2. REACT LOOP
        current_prompt = user_input
        steps = 0
        executed_actions = set()

        while steps < self.max_steps:
            res = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            
            tracker.track_request(
                provider=res.get("provider", "unknown"),
                model=self.llm.model_name,
                usage=res.get("usage", {}),
                latency_ms=res.get("latency_ms", 0)
            )
            
            response_content = res.get("content", "").strip()
            logger.log_event("LLM_RESPONSE", {"content": response_content})
            
            final_match = re.search(r"Final Answer:\s*(.*)", response_content, re.DOTALL)
            if final_match:
                final_answer = final_match.group(1).strip()
                logger.log_event("AGENT_FINAL_ANSWER", {"answer": final_answer, "steps": steps + 1})
                logger.log_event("AGENT_END", {"steps": steps + 1})
                return final_answer
            
            # 3. CASCADE PARSER
            response_clean = re.sub(r"```(python|json|markdown)?", "", response_content)
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", response_clean)
            if not action_match:
                action_match = re.search(r"(\w+)\((.*)\)", response_clean)
                
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                logger.log_event("TOOL_CALL", {"tool": tool_name, "args": tool_args})
                
                # 4. REPETITIVE ACTION BLOCKER
                action_sig = (tool_name, tool_args.lower())
                if action_sig in executed_actions:
                    observation = "Error: You have already executed this action with these exact parameters. Do not repeat the same action. Modify your parameters or proceed to Final Answer."
                    logger.log_event("REPETITIVE_ACTION_BLOCKED", {"tool": tool_name, "args": tool_args})
                else:
                    executed_actions.add(action_sig)
                    observation = self._execute_tool(tool_name, tool_args)
                
                logger.log_event("TOOL_OBSERVATION", {"tool": tool_name, "observation": observation})
                
                action_idx = response_content.find("Action:")
                if action_idx == -1:
                    action_idx = response_content.find(tool_name + "(")
                
                end_line_idx = response_content.find("\n", action_idx)
                if end_line_idx == -1:
                    clean_res = response_content
                else:
                    clean_res = response_content[:end_line_idx]
                
                current_prompt += f"\n{clean_res}\nObservation: {observation}"
            else:
                logger.log_event("AGENT_PARSING_ERROR", {"response": response_content})
                if steps == self.max_steps - 1:
                    logger.log_event("AGENT_END", {"steps": steps + 1})
                    return response_content
                
                current_prompt += f"\n{response_content}\nThought: I must output a valid Action: tool_name(params) or Final Answer: response."
                
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps})
        return "Failed to find a final answer within the maximum steps."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool['name'] == tool_name:
                try:
                    kwargs = {}
                    import json
                    try:
                        parsed = json.loads(args)
                        if isinstance(parsed, dict):
                            kwargs = parsed
                    except Exception:
                        pass
                    
                    if not kwargs:
                        pairs = re.findall(r"(\w+)\s*=\s*(?:['\"](.*?)['\"]|([^\s,]+))", args)
                        for key, str_val, raw_val in pairs:
                            val = str_val if str_val else raw_val
                            val = val.strip("'\"")
                            if val.lower() == "true":
                                kwargs[key] = True
                            elif val.lower() == "false":
                                kwargs[key] = False
                            else:
                                try:
                                    if '.' in val:
                                        kwargs[key] = float(val)
                                    else:
                                        kwargs[key] = int(val)
                                except ValueError:
                                    kwargs[key] = val
                    
                    func = tool['func']
                    result = func(**kwargs)
                    return str(result)
                except Exception as e:
                    return f"Error executing tool '{tool_name}': {str(e)}"
        return f"Tool '{tool_name}' not found."

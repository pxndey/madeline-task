
from models.models import UserRequest, State
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import re
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END





def call_agent(
        request: UserRequest
):
    """
    Research agent that:
    1. Expands the user's question
    2. Generates search queries
    3. Executes web searches
    4. Summarizes results
    
    Args:
        request: The research question to answer
        
    Returns:
        str: The summarized answer with sources
    """
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    load_dotenv()
    print(os.getenv("GOOGLE_API_KEY"))
    print(os.getenv("TAVILY_API_KEY"))
    query = request.query

    # 1. Initialize components
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
        )
    search_tool = TavilySearchResults(max_results=3,)

    # 3. Define node functions
    def expand_question(state: State):
        prompt = f"""
        Expand this user question to be more comprehensive and detailed:
        Original: {state['original_question']}
        
        Consider:
        - Adding relevant context
        - Clarifying ambiguous terms
        - Including implicit assumptions
        """
        expanded = llm.invoke(prompt)
        return {"expanded_question": expanded.content}



    def generate_queries(state: State):
        prompt = f"""
        Generate 3 optimal search engine queries to research:
        {state['expanded_question']}
        
        Return ONLY a numbered list of search queries in this exact format:
        1. First search query
        2. Second search query
        3. Third search query
        """
        response = llm.invoke(prompt)
        
        # Robust extraction with regex
        queries = []
        for line in response.content.split('\n'):
            match = re.match(r'^\d+\.\s+(.+)$', line.strip())
            if match:
                queries.append(match.group(1))
        
        # Fallback if numbering fails
        if not queries:
            queries = [q.strip() for q in response.content.split('\n') if q.strip()]
        
        return {"search_queries": queries[:3]}  # Ensure max 3 queries



    def execute_searches(state: State):
        all_results = []
        for query in state["search_queries"]:
            try:
                results = search_tool.invoke({"query": query})
                if results:  # Only add if we got results
                    all_results.extend(results)
            except Exception as e:
                print(f"Error searching for {query}: {e}")
        return {"search_results": all_results}



    def summarize_results(state: State):
        prompt = f"""
        Original question: {state['original_question']}
        
        Research results:
        {state['search_results']}
        
        Provide a comprehensive answer:
        1. Directly answer the original question
        2. Cite sources using [1], [2] formatting
        3. Highlight key findings
        4. Note limitations or uncertainties
        """
        summary = llm.invoke(prompt)
        return {"messages": [{"role": "assistant", "content": summary.content}]}



    # 4. Build workflow
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("expand", expand_question)
    workflow.add_node("generate_queries", generate_queries)
    workflow.add_node("search", execute_searches)
    workflow.add_node("summarize", summarize_results)

    # Define flow
    workflow.add_edge("expand", "generate_queries")
    workflow.add_edge("generate_queries", "search")
    workflow.add_edge("search", "summarize")

    # Set entry and exit points
    workflow.add_edge(START, "expand")
    workflow.add_edge("summarize", END)

    # 5. Compile and execute
    app = workflow.compile()
    
    # Run with initial state
    result = app.invoke({
        "original_question": query,
        "messages": []
    })
    print(result)
    return result

# Example usage
if __name__ == "__main__":
    answer = call_agent("What's the latest research on LLM agent architectures?")
    print("Research Result:\n")
    print(answer)
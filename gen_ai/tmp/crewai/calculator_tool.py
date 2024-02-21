from langchain.tools import tool


class CalculatorTools():

  @tool("math_agent_tool")
  def calculate(operation):
    """Useful to perform any mathematical calculations, 
    like sum, minus, multiplication, division, etc.
    The input to this tool should be a mathematical 
    expression, a couple examples are `200*7` or `5000/2*10`
    """
    math_results = eval(operation)
    return math_results
from comparison_openai_agents.tools import calculate, get_weather
def test_tools_have_names(): assert calculate.name == 'calculate' and get_weather.name == 'get_weather'

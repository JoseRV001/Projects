import anthropic
import requests
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

#main api url used in the ai_poekdex_app
POKEAPI = "https://pokeapi.co/api/v2"

#system prompt for the agen, gives it instructions and rules on how it will be utilized, for both anthropic and openai
SYSTEM_PROMPT = """You are PokéDex AI, an expert Pokémon identifier. Your sole purpose is to identify Pokémon based on user descriptions.

When a user describes a Pokémon (appearance, abilities, type, behaviour, habitat, move, etc.):
1. Use the search_pokemon tool to look up candidates by name or keyword.
2. Use the get_pokemon tool to fetch full details (types, stats, abilities, height, weight, sprite).
3. Use get_pokemon_species for flavour text and habitat info if needed.
4. Cross-reference the fetched data with the user's description and identify the best match.
5. Present your answer clearly: state the Pokémon's name, explain WHY it matches the description, and share a fun fact.

Rules:
- Always use the tools to verify — never guess purely from memory.
- If multiple Pokémon could match, name them all and explain the differences.
- If you cannot identify it, ask the user for more clues.
- Keep responses friendly, enthusiastic, and concise.
- Do NOT discuss topics unrelated to Pokémon."""

# Tool deinitions for Anthropic agent
TOOL_DEFS_ANTHROPIC = [
    {"name": "search_pokemon",
     "description": "Search for a Pokémon by name or keyword. Returns basic info and confirms if it exists.",
     "input_schema": {"type": "object",
                      "properties": {"name_or_keyword": {"type": "string", "description": "Pokémon name or close guess"}},
                      "required": ["name_or_keyword"]}},
    {"name": "get_pokemon",
     "description": "Fetch full Pokémon details: types, abilities, stats, height, weight, moves, sprite URL.",
     "input_schema": {"type": "object",
                      "properties": {"name_or_id": {"type": "string", "description": "Pokémon name or Pokédex ID"}},
                      "required": ["name_or_id"]}},
    {"name": "get_pokemon_species",
     "description": "Fetch species info: Pokédex flavour text, habitat, generation, legendary/mythical status.",
     "input_schema": {"type": "object",
                      "properties": {"name_or_id": {"type": "string", "description": "Pokémon name or ID"}},
                      "required": ["name_or_id"]}},
    {"name": "get_type_info",
     "description": "Get damage relations for a Pokémon type.",
     "input_schema": {"type": "object",
                      "properties": {"type_name": {"type": "string", "description": "e.g. fire, psychic, dragon"}},
                      "required": ["type_name"]}},
    {"name": "get_ability_info",
     "description": "Get description of a Pokémon ability and list Pokémon that have it.",
     "input_schema": {"type": "object",
                      "properties": {"ability_name": {"type": "string", "description": "e.g. intimidate, levitate"}},
                      "required": ["ability_name"]}},
]

#Tool deinitions for OpenAI agent
TOOL_DEFS_OPENAI = [
    {"type": "function", "function": {
        "name": "search_pokemon",
        "description": "Search for a Pokémon by name or keyword. Returns basic info and confirms if it exists.",
        "parameters": {"type": "object",
                       "properties": {"name_or_keyword": {"type": "string", "description": "Pokémon name or close guess"}},
                       "required": ["name_or_keyword"]}}},
    {"type": "function", "function": {
        "name": "get_pokemon",
        "description": "Fetch full Pokémon details: types, abilities, stats, height, weight, moves, sprite URL.",
        "parameters": {"type": "object",
                       "properties": {"name_or_id": {"type": "string", "description": "Pokémon name or Pokédex ID"}},
                       "required": ["name_or_id"]}}},
    {"type": "function", "function": {
        "name": "get_pokemon_species",
        "description": "Fetch species info: Pokédex flavour text, habitat, generation, legendary/mythical status.",
        "parameters": {"type": "object",
                       "properties": {"name_or_id": {"type": "string", "description": "Pokémon name or ID"}},
                       "required": ["name_or_id"]}}},
    {"type": "function", "function": {
        "name": "get_type_info",
        "description": "Get damage relations for a Pokémon type.",
        "parameters": {"type": "object",
                       "properties": {"type_name": {"type": "string", "description": "e.g. fire, psychic, dragon"}},
                       "required": ["type_name"]}}},
    {"type": "function", "function": {
        "name": "get_ability_info",
        "description": "Get description of a Pokémon ability and list Pokémon that have it.",
        "parameters": {"type": "object",
                       "properties": {"ability_name": {"type": "string", "description": "e.g. intimidate, levitate"}},
                       "required": ["ability_name"]}}},
]


#Main poke api function tools
#makes the request to the api and returns the response as json
def api_get(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

#tool to search for a pokemon if it exsists, by name or keyword
def tool_search_pokemon(name_or_keyword):
    slug = name_or_keyword.lower().strip().replace(" ", "-")
    data = api_get(f"{POKEAPI}/pokemon/{slug}")
    if "error" not in data:
        return json.dumps({"found": True, "id": data["id"], "name": data["name"],
                           "types": [t["type"]["name"] for t in data["types"]]})
    species = api_get(f"{POKEAPI}/pokemon-species/{slug}")
    if "error" not in species:
        return json.dumps({"found": True, "name": species["name"], "id": species["id"]})
    return json.dumps({"found": False, "tried": slug,
                       "hint": "Try a different spelling or a related keyword."})

#tool to get the full stats of the pokemon(type,abilities,and sprite)
#the sprite gets displayed in the UI
def tool_get_pokemon(name_or_id):
    slug = str(name_or_id).lower().strip().replace(" ", "-")
    data = api_get(f"{POKEAPI}/pokemon/{slug}")
    if "error" in data:
        return json.dumps(data)
    return json.dumps({
        "id": data["id"], "name": data["name"],
        "types": [t["type"]["name"] for t in data["types"]],
        "abilities": [a["ability"]["name"] for a in data["abilities"]],
        "height_dm": data["height"], "weight_hg": data["weight"],
        "base_stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
        "moves_sample": [m["move"]["name"] for m in data["moves"][:10]],
        "sprite": data["sprites"]["front_default"],
    })

#tool to get the flavor text, habitat, legendary status
def tool_get_pokemon_species(name_or_id):
    slug = str(name_or_id).lower().strip().replace(" ", "-")
    data = api_get(f"{POKEAPI}/pokemon-species/{slug}")
    if "error" in data:
        return json.dumps(data)
    flavour = next(
        (e["flavor_text"].replace("\n", " ").replace("\f", " ")
         for e in data["flavor_text_entries"] if e["language"]["name"] == "en"),
        "No flavour text found."
    )
    return json.dumps({
        "name": data["name"],
        "habitat": data["habitat"]["name"] if data["habitat"] else "unknown",
        "generation": data["generation"]["name"],
        "is_legendary": data["is_legendary"], "is_mythical": data["is_mythical"],
        "flavor_text": flavour,
        "genera": next((g["genus"] for g in data["genera"] if g["language"]["name"] == "en"), ""),
    })

#tool to get the damage relations for the type of the pokemon
def tool_get_type_info(type_name):
    data = api_get(f"{POKEAPI}/type/{type_name.lower().strip()}")
    if "error" in data:
        return json.dumps(data)
    dr = data["damage_relations"]
    return json.dumps({
        "type": type_name,
        "double_damage_to":   [t["name"] for t in dr["double_damage_to"]],
        "half_damage_to":     [t["name"] for t in dr["half_damage_to"]],
        "double_damage_from": [t["name"] for t in dr["double_damage_from"]],
        "half_damage_from":   [t["name"] for t in dr["half_damage_from"]],
        "no_damage_from":     [t["name"] for t in dr["no_damage_from"]],
    })

#tool to get the description of the ability and the first 8 pokemon assosicated with it
def tool_get_ability_info(ability_name):
    slug = ability_name.lower().strip().replace(" ", "-")
    data = api_get(f"{POKEAPI}/ability/{slug}")
    if "error" in data:
        return json.dumps(data)
    effect = next(
        (e["short_effect"] for e in data["effect_entries"] if e["language"]["name"] == "en"),
        "No description."
    )
    return json.dumps({
        "ability": data["name"], "effect": effect,
        "notable_pokemon": [p["pokemon"]["name"] for p in data["pokemon"][:8]],
    })

#dictionary that maps tool names to their corresponding functions, used by both agents to execute function calls
TOOL_FN = {
    "search_pokemon":      lambda i: tool_search_pokemon(i["name_or_keyword"]),
    "get_pokemon":         lambda i: tool_get_pokemon(i["name_or_id"]),
    "get_pokemon_species": lambda i: tool_get_pokemon_species(i["name_or_id"]),
    "get_type_info":       lambda i: tool_get_type_info(i["type_name"]),
    "get_ability_info":    lambda i: tool_get_ability_info(i["ability_name"]),
}


# Claude - Anthropic Agent

def chat_with_claude(api_key, model, max_tokens, temperature, messages):
    """
    Run the agentic loop with Claude (Anthropic).

    Args:
        api_key (str): Anthropic API key.
        model (str): Model name.
        max_tokens (int): Max tokens per call.
        temperature (float): Sampling temperature (0.0–1.0).
        messages (list): Conversation history [{role, content}].

    Returns:
        tuple: (final_text, tool_calls_log, found_pokemon)
    """
    client = anthropic.Anthropic(api_key=api_key)
    history = [{"role": m["role"], "content": m["content"]} for m in messages]

    kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=SYSTEM_PROMPT,
        messages=history,
        tools=TOOL_DEFS_ANTHROPIC,
    )

    tool_calls_log = []
    final_text = ""
    found_pokemon = None
    #the response content is a list of blocks, this will separate the text blocks from the response
    #Claude's words are the turn text, and the tool_uses is used to call the function and get the results
    while True:
        response = client.messages.create(**kwargs)
        turn_text, tool_uses = "", []
        for block in response.content:
            if block.type == "text":
                turn_text += block.text
            elif block.type == "tool_use":
                tool_uses.append(block)
        #if there are no tool uses, then Claude is done reasoning and the final answer is received
        if not tool_uses:
            final_text = turn_text
            break
        #if there are tool calls,python looks up the function and calls the right one for the tool
        #tu.input is the dictionary of the auguments the model passes
        tool_result_content = []
        for tu in tool_uses:
            fn = TOOL_FN.get(tu.name)
            result = fn(tu.input) if fn else json.dumps({"error": "unknown tool"})
            if tu.name == "get_pokemon":
                try:
                    parsed = json.loads(result)
                    if parsed.get("sprite"):
                        found_pokemon = parsed
                except Exception:
                    pass
            tool_calls_log.append((tu.name, tu.input, result))
            tool_result_content.append({"type": "tool_result", "tool_use_id": tu.id, "content": result})

        kwargs["messages"] = kwargs["messages"] + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_result_content},
        ]

    return final_text, tool_calls_log, found_pokemon


#ChatGPT - OpenAI Agent

def chat_with_openai(api_key, model, max_tokens, temperature, messages):
    """
    Run the agentic loop with an OpenAI model.

    Args:
        api_key (str): OpenAI API key.
        model (str): Model name (e.g. gpt-4o).
        max_tokens (int): Max tokens per call.
        temperature (float): Sampling temperature (0.0–2.0).
        messages (list): Conversation history [{role, content}].

    Returns:
        tuple: (final_text, tool_calls_log, found_pokemon)
    """
    if OpenAI is None:
        raise ImportError("openai package is not installed. Run: pip install openai")

    client = OpenAI(api_key=api_key)
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history += [{"role": m["role"], "content": m["content"]} for m in messages]

    tool_calls_log = []
    final_text = ""
    found_pokemon = None

    while True:
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=history,
            tools=TOOL_DEFS_OPENAI,
            tool_choice="auto",
        )

        message = response.choices[0].message
        tool_uses = message.tool_calls or []

        if not tool_uses:
            final_text = message.content or ""
            break

        # Append assistant turn with tool calls to history
        history.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in tool_uses
            ],
        })

        for tc in tool_uses:
            fn = TOOL_FN.get(tc.function.name)
            input_args = json.loads(tc.function.arguments)
            result = fn(input_args) if fn else json.dumps({"error": "unknown tool"})
            if tc.function.name == "get_pokemon":
                try:
                    parsed = json.loads(result)
                    if parsed.get("sprite"):
                        found_pokemon = parsed
                except Exception:
                    pass
            tool_calls_log.append((tc.function.name, input_args, result))
            history.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return final_text, tool_calls_log, found_pokemon
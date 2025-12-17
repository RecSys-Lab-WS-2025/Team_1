"""
Story generation service for creating Harry Potter themed adventure narratives.

This module implements direct story generation (no LLM calls):
- Step A: Generate story skeleton (Outline + Prologue + Epilogue)
- Step B: Generate all breakpoint content (Main Quest chapters, ~1000 words each)
- Step C: Generate mini quests for each breakpoint

All generated content is in English as per project requirements.
"""
import json
import random
import os
from pathlib import Path
from typing import Any, Optional

from app.models.entities import Route, Breakpoint


# Path to historical context data
HISTORICAL_CONTEXT_DIR = Path(__file__).parent.parent.parent / "data" / "historical_context"


def _load_historical_context(route_id: int) -> Optional[dict[int, dict[str, Any]]]:
    """
    Load historical context for a specific route.
    
    Args:
        route_id: Route ID to load context for
    
    Returns:
        Dictionary mapping order_index to historical context, or None if not found
    """
    context_file = HISTORICAL_CONTEXT_DIR / f"route_{route_id}.json"
    if not context_file.exists():
        return None
    
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert to dict indexed by order_index
            context_map = {}
            for bp in data.get('breakpoints', []):
                context_map[bp['order_index']] = bp.get('historical_context', '')
            return context_map
    except Exception as e:
        print(f"⚠️ Failed to load historical context: {e}")
        return None


def _generate_harry_potter_skeleton(route_context: dict) -> dict:
    """
    Generate Harry Potter themed story skeleton.
    
    Args:
        route_context: Formatted route information
    
    Returns:
        dict with title, outline, prologue, epilogue
    """
    route_name = route_context.get('name', 'Unknown Location')
    location = route_context.get('location', 'a mysterious place')
    
    # Generate title
    title = f"The Historical Mysteries of {route_name}"
    
    # Generate outline
    outline = f"A young wizard embarks on an educational quest to discover how Muggle history and magical protection are intertwined at {route_name}, learning that understanding the past is key to preserving the future."
    
    # Generate prologue
    prologue = f"""You sit in the Hogwarts library, studying for your History of Magic exam, when Professor McGonagall approaches your table. She's holding an ancient leather-bound journal and a sealed letter bearing the symbol of the Order of the Phoenix.

"I have a special assignment for you," she says, her expression serious but kind. "The Order has discovered that several historically significant Muggle locations are under threat from dark wizards who seek to sever the magical protections that have been woven into these places over centuries."

She hands you the journal. "This is a Historical Seeker's Journal. It will reveal hidden historical knowledge at each location you visit. Your mission is not one of combat, but of understanding. You must journey to {route_name} in {location} and learn the true history of each significant point along the route."

"But why me, Professor?" you ask.

"Because," she replies with a slight smile, "you've shown exceptional ability in understanding the connection between Muggle and magical worlds. This quest requires someone who can appreciate history—both magical and Muggle—and understand how they're intertwined."

She places the sealed letter on top of the journal. "The Order of Phoenix has identified specific locations along {route_name} where the boundary between historical significance and magical protection is strongest. At each location, you'll use this journal to uncover the true history. That knowledge itself will be your greatest tool."

"Dark wizards seek to corrupt these places not by attacking them directly, but by severing their connection to history—erasing the memories and significance that give them magical protection. By learning and understanding the history, you strengthen those protections."

You accept the journal and letter, feeling the weight of responsibility. This isn't just about magic—it's about preserving the stories and memories that make places significant.

"Remember," Professor McGonagall adds as she turns to leave, "history is not just dates and facts. It's the accumulated emotions, experiences, and significance that humans attach to places. That emotional resonance creates magical energy. Understand the history, and you'll understand the magic."

Your adventure begins not with a wand duel, but with an open mind and a willingness to learn."""
    
    # Generate epilogue
    epilogue = f"""As you stand at the final location along {route_name}, the Historical Seeker's Journal glowing softly in your hands, you reflect on everything you've learned.

This quest was unlike any other. You didn't battle dark wizards with spells—instead, you defeated them by understanding, by learning, by connecting with the deep history of each place you visited. Each location told you its story: the people who gathered there, the events that shaped it, the traditions that have been passed down through generations.

You've discovered that the greatest magical protection doesn't come from powerful enchantments or ancient artifacts—it comes from human memory, from the significance that people attach to places, from the accumulated weight of history and emotion.

The dark wizards sought to sever these connections, to make these places "just locations" devoid of meaning. But by learning and understanding the true history, you've strengthened the magical protections that have guarded these places for centuries.

You've learned about {route_name} in ways that no textbook could teach. You've seen how Muggle history and magical guardianship are not separate things, but two perspectives on the same truth. You understand now why Hermione always insisted that "knowledge is power"—not because facts make you strong, but because understanding creates connection, and connection creates protection.

As you prepare to return to Hogwarts, you know that you'll remember every story, every historical detail, every moment of significance you discovered. These aren't just facts for an exam—they're living memories that you now carry with you, adding your own layer of protection and understanding to these special places.

Professor McGonagall was right: this quest required not combat skills but something far more valuable—the ability to listen, to learn, and to understand the deep connections between past and present, between Muggle and magical, between history and protection.

Your Historical Seeker's Journal is now full of glowing entries, each one a testament to the places you've visited and the stories you've learned. The dark threat has been neutralized not by destruction, but by preservation—by ensuring that these histories continue to be known, remembered, and honored.

Your quest is complete. You've proven that sometimes the most powerful magic is simply understanding and remembering the truth."""
    
    return {
        "title": title,
        "outline": outline,
        "prologue": prologue,
        "epilogue": epilogue
    }


def _generate_harry_potter_chapter(
    chapter_num: int,
    total_chapters: int,
    poi_name: str,
    poi_type: str,
    historical_context: Optional[str],
    previous_chapter_summary: str = "",
    next_location_hint: str = "",
    is_wiesn_route: bool = False
) -> str:
    """
    Generate a ~1000 word Harry Potter themed chapter for a breakpoint.
    Focus on presenting historical context through storytelling.
    
    Args:
        chapter_num: Chapter number (0-indexed)
        total_chapters: Total number of chapters
        poi_name: Name of the POI/breakpoint
        poi_type: Type of the POI
        historical_context: Historical context for this location (if available)
        previous_chapter_summary: Brief summary of previous chapter for continuity
        next_location_hint: Hint about next location
        is_wiesn_route: Whether this is the Wiesn route (for detailed generation)
    
    Returns:
        Full chapter text (~1000 words for Wiesn, shorter for others)
    """
    # Base chapter structure
    chapter_intro = f"""Chapter {chapter_num + 1}: The Secrets of {poi_name}

"""
    
    # For non-Wiesn routes, use simple mock data
    if not is_wiesn_route:
        return _generate_simple_mock_chapter(
            chapter_num, poi_name, poi_type, previous_chapter_summary, next_location_hint
        )
    
    # For Wiesn route, generate detailed content with historical context as the centerpiece
    if historical_context:
        # Opening - Arrival and sensing the history
        opening = f"""You arrive at {poi_name}, your magical compass guiding you to this precise location. {previous_chapter_summary if previous_chapter_summary else "The ancient map from the Order of Phoenix glows softly in your hand,"} revealing that this place holds secrets crucial to your quest.

As you approach, your wand grows warm—a sign that powerful magic is woven into the very foundations of this location. But this is not the dark, foreboding magic you've been warned about. Instead, it feels like the magic of memory itself, as if the stones and air have absorbed centuries of human history and are now ready to share their stories.

You pull out the enchanted journal given to you by Professor McGonagall. "When you seek magical artifacts," she had told you, "you must first understand the Muggle history of the place. For our magical world and theirs are more intertwined than most realize. The truth lies in the intersection."

Opening the journal, you find a page dedicated to {poi_name}, written in glowing ink that appears only when you're at the location itself. You read aloud, and as you do, the words seem to come alive:

"""

        # Historical context as discovered knowledge - this is the core of the chapter
        historical_discovery = f""""{historical_context}"

As you finish reading, the air around you shimmers. The journal's magic creates ethereal images—like moving photographs but translucent, showing you glimpses of the past. You watch, mesmerized, as history unfolds before your eyes.

You see the people who once walked here, the events that shaped this place, the traditions that have been passed down through generations. But through your wizard's sight, you also perceive something more: faint traces of magical influence woven throughout these historical moments. 

The wizarding community has always been here, you realize, hidden in plain sight, subtly guiding and protecting, ensuring that these important historical moments could unfold as they were meant to. The Muggles built this place and created its history, but wizards were the silent guardians, preserving the magic that makes certain places special.

You notice specific details in the ethereal visions that only a trained wizard would recognize: a subtle wand movement disguised as a gesture, a protective charm hidden in the architecture, enchantments woven into celebrations that Muggles experience as inexplicable feelings of joy and wonder.

"Remarkable, isn't it?" a voice says behind you.

"""

        # The encounter and deeper historical revelation
        encounter = f"""You turn to see an elderly witch approaching, wearing elegant traveling robes adorned with brass timepiece medallions. She introduces herself as Madam Tempus, a Historian of Magical-Muggle Convergence from the Department of Mysteries.

"The Order of Phoenix sent word you'd be coming," she says kindly. "I've been the guardian of {poi_name} for forty years. Let me share what the journal cannot."

She waves her wand, and the ethereal images grow clearer, more detailed. "You see," she explains, "this location isn't just historically significant to Muggles. It's a nexus point—a place where the boundary between our world and theirs grows thin, not because of dark magic, but because of collective human emotion and memory."

Madam Tempus points to various elements of the location as she speaks. "Every celebration, every gathering, every moment of joy or solemnity that Muggles experience here creates ripples of magical energy. Over centuries, these ripples have accumulated, creating a reservoir of protective magic. This is what dark wizards seek to corrupt—not for the power itself, but to sever the connection between Muggle history and magical protection."

She hands you a small crystalline artifact. "This is a Memory Stone. It has absorbed fragments of every significant moment at this location. To find the next piece of your quest, you must attune yourself to its resonance. Close your eyes, hold the stone, and let the history speak to you."

"""

        # The test - understanding and connecting with history
        historical_challenge = f"""You follow her instructions, closing your eyes and focusing on the Memory Stone. Immediately, you're overwhelmed by sensations—voices, music, laughter, solemnity, celebration. Centuries of human experience flow through you.

But you remember Professor Flitwick's lessons on magical meditation. You steady your breathing and instead of being swept away by the torrent of memories, you begin to understand them. You see how each historical event at {poi_name} contributed to the magical energy here. You understand why this place matters—not just to Muggles, but to the preservation of magical-Muggle harmony.

The test becomes clear: you must identify the single most magically significant historical moment at this location. The Memory Stone pulses with different colored lights, each representing a different era, a different event.

You think carefully about everything you've learned. The historical facts are clear in your mind: {historical_context[:200]}{"..." if len(historical_context) > 200 else ""}

Drawing on both your knowledge of history and your magical intuition, you focus on the moment that resonates most strongly with magical energy. The Memory Stone flashes brilliant gold, confirming your understanding.

"Well done," Madam Tempus says with approval. "You've grasped what many wizards never understand: that Muggle history isn't separate from magical history—they're two threads of the same tapestry. By understanding and respecting the Muggle history of this place, you've proven yourself worthy of the magical knowledge it guards."

"""

        # Resolution with forward momentum
        resolution = f"""The Memory Stone transforms in your hand, becoming a compass that points steadily toward {next_location_hint if next_location_hint else "the next location"}. 

"The path forward is revealed," Madam Tempus says. "But remember: each location you visit has its own story, its own convergence of Muggle history and magical significance. Honor both, and you'll succeed in your quest. The dark wizards seek to destroy these connections, to separate magic from human history. You must preserve them."

She begins to fade, her duty at this location complete for now. "One more thing," she calls out as she disappears. "The history you've learned here isn't just facts—it's the foundation of understanding why these places must be protected. Carry that knowledge with you."

You stand for a moment longer at {poi_name}, looking at it with new eyes. What once seemed like simply a historically significant place now reveals itself as so much more—a living testament to the intersection of human achievement and magical wonder.

With renewed purpose, you consult your new compass and prepare to journey to {next_location_hint if next_location_hint else "your next destination"}. Each step of this quest deepens your understanding of how intertwined the magical and Muggle worlds truly are. And somewhere ahead lies the artifact that dark forces seek—an artifact whose true power lies not in magic alone, but in its connection to centuries of human history.

Your adventure continues, guided by history and magic alike..."""

        # Combine all parts with history at the center
        full_chapter = chapter_intro + opening + historical_discovery + encounter + historical_challenge + resolution
        
        return full_chapter
        
    else:
        # Fallback for breakpoints without historical context
        opening = f"""You arrive at {poi_name}, sensing magical energy in the air. Your quest continues, though without detailed historical records, you must rely on your magical intuition to uncover the secrets hidden here.

"""
        return chapter_intro + opening + "The magical trail leads you forward, toward new discoveries and challenges..."


def _generate_simple_mock_chapter(
    chapter_num: int,
    poi_name: str,
    poi_type: str,
    previous_chapter_summary: str = "",
    next_location_hint: str = ""
) -> str:
    """
    Generate a simple mock chapter for non-Wiesn routes.
    
    Args:
        chapter_num: Chapter number (0-indexed)
        poi_name: Name of the POI/breakpoint
        poi_type: Type of the POI
        previous_chapter_summary: Brief summary of previous chapter
        next_location_hint: Hint about next location
    
    Returns:
        Simple chapter text (~200-300 words)
    """
    chapter_intro = f"""Chapter {chapter_num + 1}: {poi_name}

"""
    
    content = f"""{previous_chapter_summary if previous_chapter_summary else "Following your magical quest,"} you arrive at {poi_name}. 

As a wizard exploring this {poi_type}, you immediately sense the magical energy that flows through this place. Your wand responds to the ancient magic that has been woven into the very fabric of this location over the centuries.

You take a moment to observe your surroundings. The magical signature here is strong, indicating that this place has been touched by powerful wizarding events in the past. You can feel the presence of ancient spells and enchantments that have been layered upon this location.

Following the guidance from the Order of Phoenix, you search for clues and magical markers. Your training at Hogwarts has prepared you well for this moment. You know how to recognize the signs of hidden magic, how to read the magical traces left behind by previous wizards.

After a thorough investigation, you discover a small magical artifact—a token that will guide you to your next destination. The artifact glows softly in your hand, pointing toward {next_location_hint if next_location_hint else "the next location on your quest"}.

You've made progress, but the journey continues. The real challenges and mysteries lie ahead, waiting to be uncovered by a worthy wizard.

The adventure continues..."""
    
    return chapter_intro + content


def _generate_mini_quests(
    chapter_num: int,
    total_chapters: int,
    poi_name: str,
    poi_type: str
) -> list[dict[str, Any]]:
    """
    Generate 1-2 mini quests for a breakpoint.
    
    Args:
        chapter_num: Chapter number (0-indexed)
        total_chapters: Total number of chapters
        poi_name: Name of the POI/breakpoint
        poi_type: Type of the POI
    
    Returns:
        List of mini quest dicts with task_description and xp_reward
    """
    # Quest types with Harry Potter themed descriptions
    quest_templates = {
        "photo": {
            "descriptions": [
                f"Use your enchanted camera to capture the magical essence of {poi_name}. The photograph will reveal hidden magical properties invisible to Muggles.",
                f"Take a magical photograph of {poi_name} using the special camera provided by the Order of Phoenix. The image will help document your quest.",
                f"Capture the mystical aura of {poi_name} with your enchanted camera. This magical photograph will be added to your collection of evidence."
            ],
            "base_xp": 15,
            "type": "photo"
        },
        "observation": {
            "descriptions": [
                f"Carefully observe {poi_name} and identify any magical signatures or hidden enchantments. Use your magical sight to see what Muggles cannot.",
                f"Examine {poi_name} closely for signs of ancient magic. Look for runes, magical symbols, or traces of spellwork that might reveal secrets.",
                f"Study the magical properties of {poi_name}. Your trained eye can spot details that will be crucial to solving the mystery."
            ],
            "base_xp": 20
        },
        "collection": {
            "descriptions": [
                f"Collect magical evidence from {poi_name}. Look for enchanted objects, magical traces, or clues left behind by previous wizards.",
                f"Gather magical artifacts or clues hidden at {poi_name}. These items will help you piece together the puzzle of your quest.",
                f"Search for and collect any magical items or traces at {poi_name}. Each piece of evidence brings you closer to the truth."
            ],
            "base_xp": 25
        },
        "puzzle": {
            "descriptions": [
                f"Solve the magical puzzle hidden at {poi_name}. The solution requires combining your knowledge of magic with the history of this location.",
                f"Decipher the ancient riddle or puzzle at {poi_name}. Your wizarding education has prepared you for this challenge.",
                f"Unlock the magical mystery at {poi_name} by solving the puzzle. The answer lies in understanding both magic and history."
            ],
            "base_xp": 30,
            "generate_quiz": True  # Flag to generate actual quiz
        }
    }
    
    # Determine number of quests (1-2, with higher chance of 2 quests for later chapters)
    num_quests = 2 if random.random() < (0.3 + chapter_num * 0.1) else 1
    num_quests = min(num_quests, 2)  # Max 2 quests
    
    # Select quest types (avoid duplicates)
    available_types = list(quest_templates.keys())
    selected_types = random.sample(available_types, num_quests)
    
    # Generate quests
    quests = []
    for quest_type in selected_types:
        template = quest_templates[quest_type]
        description = random.choice(template["descriptions"])
        
        # XP increases with chapter number (later chapters = harder quests = more XP)
        xp_multiplier = 1.0 + (chapter_num / total_chapters) * 0.5
        xp_reward = int(template["base_xp"] * xp_multiplier)
        
        quest_data = {
            "task_description": description,
            "xp_reward": xp_reward
        }
        
        # For puzzle quests, generate actual quiz question and answers
        if quest_type == "puzzle" and template.get("generate_quiz", False):
            quiz_data = _generate_quiz_question(poi_name, poi_type, chapter_num)
            # Store quiz data as JSON in task_description
            quest_data["task_description"] = json.dumps({
                "type": "quiz",
                "description": description,
                "question": quiz_data["question"],
                "choices": quiz_data["choices"],
                "correct_answer": quiz_data["correct_answer"]
            })
        # For photo quests, store type in JSON for easier parsing
        elif quest_type == "photo" and template.get("type") == "photo":
            quest_data["task_description"] = json.dumps({
                "type": "photo",
                "description": description
            })
        
        quests.append(quest_data)
    
    return quests


def _generate_quiz_question(
    poi_name: str,
    poi_type: str,
    chapter_num: int
) -> dict[str, Any]:
    """
    Generate a Harry Potter themed quiz question for puzzle quests.
    
    Args:
        poi_name: Name of the POI
        poi_type: Type of the POI
        chapter_num: Chapter number
    
    Returns:
        dict with question, choices, and correct_answer
    """
    # Quiz question templates
    quiz_templates = [
        {
            "question": f"What magical property makes {poi_name} significant to wizards?",
            "choices": [
                "It's a convergence point of ancient magical energy",
                "It's where the first wand was created",
                "It's a portal to another dimension",
                "It's where dragons once nested"
            ],
            "correct_answer": 0
        },
        {
            "question": f"Which spell would be most effective for revealing hidden magic at {poi_name}?",
            "choices": [
                "Revelio",
                "Lumos",
                "Accio",
                "Expelliarmus"
            ],
            "correct_answer": 0
        },
        {
            "question": f"What does the magical signature at {poi_name} indicate?",
            "choices": [
                "Ancient wizarding activity",
                "Recent dark magic",
                "A magical creature's presence",
                "A broken enchantment"
            ],
            "correct_answer": 0
        },
        {
            "question": f"Which Hogwarts house would be most interested in the history of {poi_name}?",
            "choices": [
                "Ravenclaw",
                "Gryffindor",
                "Slytherin",
                "Hufflepuff"
            ],
            "correct_answer": 0
        },
        {
            "question": f"What type of magical protection would be most appropriate for {poi_name}?",
            "choices": [
                "Concealment charms",
                "Fiendfyre",
                "Unforgivable Curses",
                "Love potions"
            ],
            "correct_answer": 0
        },
        {
            "question": f"According to magical theory, what makes {poi_type} locations particularly magical?",
            "choices": [
                "They accumulate magical energy over centuries",
                "They're built on ley lines",
                "They're protected by ancient guardians",
                "All of the above"
            ],
            "correct_answer": 3
        }
    ]
    
    # Select a random quiz template
    selected_quiz = random.choice(quiz_templates)
    
    return {
        "question": selected_quiz["question"],
        "choices": selected_quiz["choices"],
        "correct_answer": selected_quiz["correct_answer"]
    }


async def generate_story_for_route(
    route: Route,
    breakpoints: list[Breakpoint],
    narrative_style: str = "adventure"
) -> dict[str, Any]:
    """
    Generate complete Harry Potter themed story for a route.
    
    This function orchestrates the story generation process:
    1. Generates story skeleton (outline, prologue, epilogue)
    2. Generates content for all breakpoints (1000-word chapters)
    3. Generates mini quests for each breakpoint (1-2 quests per breakpoint)
    4. Returns assembled story data
    
    Args:
        route: Route entity with basic information
        breakpoints: List of breakpoint entities in order
        narrative_style: Story style (not used in direct generation, kept for API compatibility)
    
    Returns:
        dict containing:
            - title: Story title
            - outline: Mission summary
            - prologue: Opening chapter
            - epilogue: Closing chapter
            - breakpoints: List of breakpoint content dicts with:
                - index: Breakpoint index
                - main_quest: Chapter text (~1000 words)
                - mini_quests: List of mini quest dicts with task_description and xp_reward
    """
    # 1. Prepare context
    route_context = _format_route_info(route)
    
    # 2. Load historical context if available (for Wiesn route)
    historical_context_map = None
    if route.id == 1362610:  # Wiesn route
        historical_context_map = _load_historical_context(route.id)
    
    # 3. Generate skeleton
    skeleton = _generate_harry_potter_skeleton(route_context)
    
    # 4. Generate story chapters for each breakpoint
    story_points = []
    previous_summary = ""
    
    for i, bp in enumerate(sorted(breakpoints, key=lambda x: x.order_index)):
        # Get historical context for this breakpoint
        hist_context = None
        if historical_context_map:
            hist_context = historical_context_map.get(bp.order_index)
        
        # Get hint about next location
        next_hint = ""
        if i + 1 < len(breakpoints):
            next_bp = sorted(breakpoints, key=lambda x: x.order_index)[i + 1]
            next_hint = next_bp.poi_name or f"the next location"
        
        # Generate chapter (detailed for Wiesn route, simple mock for others)
        is_wiesn = route.id == 1362610
        chapter_text = _generate_harry_potter_chapter(
            chapter_num=i,
            total_chapters=len(breakpoints),
            poi_name=bp.poi_name or f"Location {i + 1}",
            poi_type=bp.poi_type or "location",
            historical_context=hist_context,
            previous_chapter_summary=previous_summary,
            next_location_hint=next_hint,
            is_wiesn_route=is_wiesn
        )
        
        # Generate mini quests for this breakpoint
        mini_quests = _generate_mini_quests(
            chapter_num=i,
            total_chapters=len(breakpoints),
            poi_name=bp.poi_name or f"Location {i + 1}",
            poi_type=bp.poi_type or "location"
        )
        
        # Create summary for next chapter
        previous_summary = f"After uncovering the secrets of {bp.poi_name or f'Location {i + 1}'},"
        
        story_points.append({
            "index": i,
            "main_quest": chapter_text,
            "mini_quests": mini_quests
        })
    
    # 5. Log generation
    print("\n" + "="*80)
    print("✨ HARRY POTTER STORY GENERATED")
    print("="*80)
    print(f"🗺️ Route: {route_context.get('name', 'Unknown')}")
    print(f"📖 Title: {skeleton.get('title', 'N/A')}")
    print(f"📊 Generated {len(story_points)} chapters")
    print("="*80 + "\n")
    
    # Log to UI
    from app.llm_logger import log_llm_output
    log_llm_output(
        message_type="skeleton",
        title=f"📖 Story Generated: {skeleton.get('title', 'Adventure')}",
        content=f"**Outline:** {skeleton.get('outline', 'N/A')}\n\n**Prologue:** {skeleton.get('prologue', 'N/A')[:200]}...\n\n**Epilogue:** {skeleton.get('epilogue', 'N/A')[:200]}...",
        metadata={
            "route_name": route_context.get('name', 'Unknown'),
            "narrative_style": "harry_potter",
            "title": skeleton.get('title', 'N/A')
        }
    )
    
    # 6. Assemble and return
    return {
        **skeleton,
        "breakpoints": story_points
    }


def _format_route_info(route: Route) -> dict:
    """
    Format route information for context.
    
    Args:
        route: Route entity
    
    Returns:
        dict with formatted route information
    """
    return {
        "name": route.title,
        "location": route.category_name or "Unknown",
        "distance_km": round(route.length_meters / 1000, 1) if route.length_meters else 0,
        "difficulty": route.difficulty or 0,
        "tags": json.loads(route.tags_json) if route.tags_json else [],
        "description": route.short_description or ""
    }

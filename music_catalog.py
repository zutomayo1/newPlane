"""Music metadata catalog and filter definitions used by the audio hub."""
from __future__ import annotations

from typing import Dict, List

MUSIC_FILTER_CHOICES = [
    ("all", "全部"),
    ("menu", "菜单"),
    ("explore", "探索"),
    ("combat", "战斗"),
    ("boss", "Boss战"),
]


def _entry(display: str, mood: str, bpm: int, length: str, tags: List[str], description: str) -> Dict[str, object]:
    return {
        "display_name": display,
        "mood": mood,
        "bpm": bpm,
        "length_hint": length,
        "tags": tags,
        "description": description,
    }


MUSIC_TRACK_METADATA: Dict[str, Dict[str, object]] = {
    "normal": _entry(
        "Stellar Patrol",
        "Lightweight cruising loop",
        120,
        "01:04",
        ["explore"],
        "Default roaming underscore for neutral sectors.",
    ),
    "boss": _entry(
        "Colossus Clash",
        "High-pressure boss suite",
        170,
        "01:30",
        ["boss", "combat"],
        "Layered percussion and aggressive bass designed for flagship encounters.",
    ),
    "calm": _entry(
        "Harbor Lights",
        "Soft ambient pads",
        90,
        "01:12",
        ["menu"],
        "Warm chords and gentle pulses for relaxed navigation moments.",
    ),
    "mystery": _entry(
        "Veiled Nebula",
        "Suspenseful texture",
        100,
        "01:05",
        ["explore"],
        "Abstract motifs with airy leads, ideal for fog-of-war scenes.",
    ),
    "epic": _entry(
        "Sunspear Armada",
        "Heroic orchestration",
        150,
        "01:24",
        ["combat"],
        "Brass-like swells propelling story-driven confrontations.",
    ),
    "intense": _entry(
        "Overload Spiral",
        "Relentless pulse",
        140,
        "01:18",
        ["combat"],
        "Sawtooth bass and glitch hits for peak firefights.",
    ),
    "cyber": _entry(
        "Neon Relay",
        "Retro-future synth",
        128,
        "01:10",
        ["combat", "explore"],
        "Arpeggiated hooks echoing through cyber arenas.",
    ),
    "ethereal": _entry(
        "Aurora Bloom",
        "Floating ambient",
        80,
        "01:08",
        ["menu", "explore"],
        "Glass-like pads for calm, high-altitude panoramas.",
    ),
    "cinematic": _entry(
        "Final Assembly",
        "Story montage",
        80,
        "01:16",
        ["menu"],
        "Hybrid strings underscoring the primary menu boards.",
    ),
    "orchestra": _entry(
        "Majestic Fleet",
        "Symphonic suite",
        100,
        "01:20",
        ["menu"],
        "Staccato strings with triumphant accents for ceremonial decks.",
    ),
    "jazz": _entry(
        "Blue Docks",
        "Lounge combo",
        110,
        "01:03",
        ["menu"],
        "Electric piano riffs that fit briefing lounges.",
    ),
    "piano": _entry(
        "Quiet Hangar",
        "Solo keys",
        90,
        "01:15",
        ["menu"],
        "Minimal piano motif for reflective selections.",
    ),
    "rock": _entry(
        "Meteor Riot",
        "Arena rock",
        160,
        "01:11",
        ["combat"],
        "Crunch guitars synced with heavy drums for adrenaline rushes.",
    ),
    "ambient": _entry(
        "Ion Drift",
        "Slow atmosphere",
        60,
        "01:22",
        ["explore"],
        "Breathing textures keeping exploration grounded.",
    ),
    "electronic": _entry(
        "Circuit Rush",
        "Modern EDM",
        130,
        "01:08",
        ["combat"],
        "Crowd-pleasing drops that fuel arcade firefights.",
    ),
    "chiptune": _entry(
        "Pixel March",
        "Retro groove",
        150,
        "01:06",
        ["menu", "explore"],
        "Bit-crushed arps celebrating classic shooter roots.",
    ),
    "tribal": _entry(
        "Stoneheart Beat",
        "Percussive ritual",
        120,
        "01:09",
        ["combat"],
        "Layered hand drums signaling survivor arenas.",
    ),
    "dubstep": _entry(
        "Gravity Break",
        "Wobble assault",
        140,
        "01:07",
        ["combat"],
        "Half-time drops tailored for cloaked boss waves.",
    ),
    "synthwave": _entry(
        "Crimson Highway",
        "Retro synthwave",
        120,
        "01:18",
        ["explore", "combat"],
        "Analog sweeps perfect for ship selection showcases.",
    ),
    "metal": _entry(
        "Iron Tempest",
        "Heavy metal",
        180,
        "01:05",
        ["combat"],
        "Palm-muted riffs matching relentless bullet curtains.",
    ),
    "trance": _entry(
        "Stellar Pulse",
        "Driving trance",
        138,
        "01:16",
        ["combat"],
        "Four-on-the-floor kick with hypnotic leads for late-game pushes.",
    ),
    "orchestral_dark": _entry(
        "Black Sun Cantata",
        "Dark orchestral",
        100,
        "01:25",
        ["boss", "combat"],
        "Low brass clusters raising dread before apocalyptic bosses.",
    ),
    "funk": _entry(
        "Cargo Jam",
        "Playful funk",
        115,
        "01:02",
        ["menu", "explore"],
        "Syncopated bass and claps ideal for lighthearted views.",
    ),
    "breakbeat": _entry(
        "Photon Runner",
        "Breakbeat sprint",
        150,
        "01:09",
        ["combat"],
        "Chopped drum fills for fast-moving encounter waves.",
    ),
    "lofi": _entry(
        "Dockside Echo",
        "Lo-fi chill",
        85,
        "01:20",
        ["menu"],
        "Vinyl-soft textures that soothe between sorties.",
    ),
    "industrial": _entry(
        "Forge Tyrant",
        "Industrial march",
        130,
        "01:14",
        ["combat"],
        "Grinding machinery pulses for siege sequences.",
    ),

    # ---- Extended procedural tracks (v2 generator) ----
    "dnb": _entry(
        "Hyperlane Break",
        "Fast breakbeats",
        174,
        "01:00",
        ["combat"],
        "High-tempo drum & bass loop for sustained firefights.",
    ),
    "downtempo": _entry(
        "Low Orbit Drift",
        "Warm groove",
        92,
        "01:00",
        ["menu", "explore"],
        "Laid-back beat and soft pads for navigation and briefing screens.",
    ),
    "deep_house": _entry(
        "Deep Sector",
        "Steady pulse",
        124,
        "01:00",
        ["combat"],
        "Four-on-the-floor drive with airy layers.",
    ),
    "acid": _entry(
        "Corrosive Circuit",
        "Acid bassline",
        132,
        "01:00",
        ["combat"],
        "Resonant saw-line accents over a club-like backbone.",
    ),
    "glitch": _entry(
        "Packet Noise",
        "Erratic fragments",
        150,
        "01:00",
        ["combat"],
        "Glitch pops and chopped transients for chaotic encounters.",
    ),
    "drone": _entry(
        "Silent Hull",
        "Long pads",
        60,
        "01:00",
        ["explore"],
        "Slow-evolving drone bed for calm, reflective moments.",
    ),
    "space": _entry(
        "Vacuum Bloom",
        "Weightless ambience",
        72,
        "01:00",
        ["explore"],
        "Sparse percussion and shimmering pads for deep space travel.",
    ),
    "menu_alt": _entry(
        "Hangar Console",
        "Alt menu theme",
        84,
        "01:00",
        ["menu"],
        "Alternative menu loop with gentler percussion.",
    ),
    "boss_phase2": _entry(
        "Phase Shift",
        "High-pressure escalation",
        176,
        "01:00",
        ["boss", "combat"],
        "Faster boss loop intended for late-stage patterns.",
    ),
    "victory_fanfare": _entry(
        "Afterburner Victory",
        "Triumphant burst",
        136,
        "01:00",
        ["menu"],
        "Celebratory groove for post-combat screens.",
    ),
}


def _infer_tags(track_id: str) -> List[str]:
    lowered = track_id.lower()
    tags: List[str] = []
    if any(token in lowered for token in ("boss", "phase", "doom", "tyrant")):
        tags.append("boss")
    if any(
        token in lowered
        for token in (
            "fight",
            "battle",
            "rage",
            "metal",
            "rock",
            "break",
            "dnb",
            "house",
            "acid",
            "dubstep",
            "trance",
            "glitch",
            "industrial",
            "rush",
            "overload",
            "intense",
            "epic",
            "cyber",
        )
    ):
        if "combat" not in tags:
            tags.append("combat")
    if any(token in lowered for token in ("menu", "select", "calm", "quiet", "lofi", "lounge", "piano", "jazz", "cinematic", "orchestra", "victory")):
        tags.append("menu")
    if any(token in lowered for token in ("explore", "normal", "mystery", "ethereal", "ambient", "space", "drone", "downtempo")):
        if "explore" not in tags:
            tags.append("explore")
    if not tags:
        tags.append("explore")
    if "boss" in tags and "combat" not in tags:
        tags.append("combat")
    return tags


def _build_generic_metadata(track_id: str) -> Dict[str, object]:
    tags = _infer_tags(track_id)
    return {
        "display_name": track_id.replace("_", " ").title(),
        "mood": "Custom mix",
        "bpm": 120,
        "length_hint": "01:00",
        "tags": tags,
        "description": "Auto-generated metadata placeholder.",
    }


def resolve_music_metadata(track_id: str | None) -> Dict[str, object]:
    """Return descriptive metadata for the requested bgm id."""
    if not track_id:
        return _build_generic_metadata("unknown")
    clean_id = track_id[4:] if track_id.startswith("bgm_") else track_id
    meta = MUSIC_TRACK_METADATA.get(clean_id)
    if meta is None:
        meta = _build_generic_metadata(clean_id)
    # return a shallow copy so callers can modify safely
    resolved = dict(meta)
    resolved["tags"] = list(meta.get("tags", []))
    resolved["track_id"] = clean_id
    return resolved

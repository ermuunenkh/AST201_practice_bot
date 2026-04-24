"""
Generates HR diagram images with a single red dot and writes MC questions to test/temp.json.
Run from project root: python -m test.generate_hr_questions
IDs start at 569 (continuing from question pool which ends at 568).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.img_gen import generate_hr_diagram

START_ID = 569

_QUESTIONS = [
    {
        "dot": (18000, 0.002),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.4 White Dwarfs on the HR Diagram",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "B-type main sequence star", "B": "Red giant", "C": "White dwarf", "D": "Subgiant", "E": "Neutron star"},
        "answer":    "C",
        "explanation": "The dot sits at high surface temperature (~18,000 K) but extremely low luminosity (~10⁻³ L☉), far below the main sequence. This is the white dwarf region — hot, Earth-sized remnants of low-mass stars.",
    },
    {
        "dot": (3500, 8e4),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.3 Giants and Supergiants",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "Red dwarf", "B": "Red giant", "C": "Red supergiant", "D": "AGB star", "E": "Horizontal branch star"},
        "answer":    "C",
        "explanation": "The dot is at very low surface temperature (~3,500 K) and extremely high luminosity (~10⁵ L☉), placing it in the supergiant region. Red supergiants are the largest stars by radius and are the evolved end-state of the most massive stars.",
    },
    {
        "dot": (5778, 1.0),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.2 The Main Sequence",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "K-type main sequence star", "B": "Subgiant", "C": "F-type main sequence star", "D": "G-type main sequence star", "E": "Red giant"},
        "answer":    "D",
        "explanation": "The dot sits at ~5,778 K and 1 L☉ — exactly the solar position on the main sequence. This is a G-type (yellow dwarf) star, fusing hydrogen in its core just like our Sun.",
    },
    {
        "dot": (22000, 9000),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.2 The Main Sequence",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "O-type main sequence star", "B": "Blue supergiant", "C": "B-type main sequence star", "D": "White dwarf", "E": "A-type main sequence star"},
        "answer":    "C",
        "explanation": "The dot lies on the main sequence at ~22,000 K and ~10⁴ L☉, consistent with a B-type star. B stars are hotter and more massive than the Sun but cooler and less luminous than O-type stars.",
    },
    {
        "dot": (3200, 0.005),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.2 The Main Sequence",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "White dwarf", "B": "Red giant", "C": "K-type main sequence star", "D": "Brown dwarf", "E": "M-type main sequence star"},
        "answer":    "E",
        "explanation": "The dot is at cool temperature (~3,200 K) and very low luminosity (~5×10⁻³ L☉) on the lower main sequence. This is an M-type star (red dwarf) — the most common type of star in the galaxy.",
    },
    {
        "dot": (4500, 80),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.3 Giants and Supergiants",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "K-type main sequence star", "B": "Red giant", "C": "Red supergiant", "D": "Horizontal branch star", "E": "AGB star"},
        "answer":    "B",
        "explanation": "The dot is at ~4,500 K but ~80 L☉, far above where a K-type main sequence star would sit (~0.1 L☉). This elevated luminosity at cool temperature places it in the red giant region — a star that has exhausted its core hydrogen and expanded.",
    },
    {
        "dot": (7500, 40),
        "topic":     "TOPIC 13: LIFE CYCLE OF A SUN-LIKE STAR",
        "sub_topic": "13.4 Helium Flash and Horizontal Branch",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "A-type main sequence star", "B": "Subgiant", "C": "Horizontal branch star", "D": "Red giant", "E": "White dwarf"},
        "answer":    "C",
        "explanation": "The dot is at ~7,500 K and ~40 L☉, sitting between the main sequence and the giant branch. Horizontal branch stars are low-mass stars fusing helium in their cores after the red giant phase, forming a roughly horizontal strip on the HR diagram.",
    },
    {
        "dot": (14000, 2e5),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.3 Giants and Supergiants",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "O-type main sequence star", "B": "B-type main sequence star", "C": "Blue supergiant", "D": "Horizontal branch star", "E": "Wolf-Rayet star"},
        "answer":    "C",
        "explanation": "The dot is at ~14,000 K and ~2×10⁵ L☉, well above the main sequence luminosity at that temperature. This places it in the supergiant region. Blue supergiants are massive evolved stars with high luminosity and relatively high surface temperature.",
    },
    {
        "dot": (6000, 3),
        "topic":     "TOPIC 13: LIFE CYCLE OF A SUN-LIKE STAR",
        "sub_topic": "13.3 Subgiant and Red Giant Phases",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "G-type main sequence star", "B": "F-type main sequence star", "C": "Subgiant", "D": "Red giant", "E": "Horizontal branch star"},
        "answer":    "C",
        "explanation": "The dot sits at ~6,000 K and ~3 L☉, slightly above the main sequence luminosity expected at that temperature (~1.5 L☉). This places it in the subgiant region — stars that have exhausted core hydrogen and are beginning to expand toward the giant branch.",
    },
    {
        "dot": (4500, 0.13),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.2 The Main Sequence",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "G-type main sequence star", "B": "M-type main sequence star", "C": "Red giant", "D": "White dwarf", "E": "K-type main sequence star"},
        "answer":    "E",
        "explanation": "The dot is at ~4,500 K and ~0.13 L☉, sitting directly on the main sequence. At this temperature and luminosity, the star is a K-type (orange dwarf) main sequence star — slightly cooler and less luminous than the Sun.",
    },
    {
        "dot": (35000, 3.5e5),
        "topic":     "TOPIC 11: BUILDING THE HR DIAGRAM",
        "sub_topic": "11.2 The Main Sequence",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "Blue supergiant", "B": "B-type main sequence star", "C": "White dwarf", "D": "O-type main sequence star", "E": "Neutron star"},
        "answer":    "D",
        "explanation": "The dot is at ~35,000 K and ~3.5×10⁵ L☉, on the upper main sequence. This is an O-type star — the hottest, most massive, and most luminous type of main sequence star, with lifetimes of only a few million years.",
    },
    {
        "dot": (3800, 2000),
        "topic":     "TOPIC 13: LIFE CYCLE OF A SUN-LIKE STAR",
        "sub_topic": "13.5 Thermal Pulses and Mass Loss",
        "question":  "The red dot on the HR diagram marks the position of a star. Which of the following best describes this star?",
        "options":   {"A": "Red dwarf", "B": "Red giant", "C": "Red supergiant", "D": "AGB star", "E": "Horizontal branch star"},
        "answer":    "D",
        "explanation": "The dot is at ~3,800 K and ~2,000 L☉, above the red giant branch but below the most extreme supergiants. This is consistent with an AGB (Asymptotic Giant Branch) star — an evolved low-to-intermediate mass star fusing helium in a shell, which can be extremely luminous.",
    },
]


def main():
    Path("database/imgs").mkdir(parents=True, exist_ok=True)

    questions = []
    for i, q in enumerate(_QUESTIONS):
        qid      = START_ID + i
        filename = f"id_{qid}"
        print(f"Generating {filename}.png ...")
        img_path = generate_hr_diagram(filename, dot=q["dot"])

        questions.append({
            "id":          qid,
            "type":        "MC",
            "topic":       q["topic"],
            "sub_topic":   q["sub_topic"],
            "question":    q["question"],
            "options":     q["options"],
            "answer":      q["answer"],
            "explanation": q["explanation"],
            "image":       str(img_path),
        })

    out_json = Path("test/temp.json")
    out_json.write_text(json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. {len(questions)} questions written to {out_json}")


if __name__ == "__main__":
    main()

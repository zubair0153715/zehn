"""Zehn verification — memory/Stroop/math/2-back/grid generation and
scoring, Zehn Score math, adaptive difficulty, workout rotation,
AI-output shape validators, routes.

Run: python tests/verify.py (or ~/workspace/.venv-fc/bin/python)
Exit code 0 = all pass. No network, no key needed (AI tests only
check the no-key error path and the shape validators, never a live
call). All seeded tests are deterministic whatever day the suite runs.
"""

import os
import sys

# Force the no-key path so AI-status tests are deterministic.
for _k in ("GEMINI_API_KEY", "GEMINI_APIkey"):
    os.environ.pop(_k, None)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zehn import engine, gemini  # noqa: E402

PASS = 0
FAIL = []


def check(name, cond, extra=""):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(f"{name} {extra}")


# --- Yaad: memory ------------------------------------------------------------
r, err = engine.memory_round(1, seed=7)
check("memory L1 3 digits", err is None and r["length"] == 3
      and len(r["digits"]) == 3, str(r))
r2, _ = engine.memory_round(1, seed=7)
check("memory seeded deterministic", r["digits"] == r2["digits"])
r, err = engine.memory_round(5, seed=7)
check("memory L5 7 digits", err is None and r["length"] == 7)
_, err = engine.memory_round(0)
check("memory level 0 rejected", err is not None)
_, err = engine.memory_round(6)
check("memory level 6 rejected", err is not None)

# hand-computed scoring: 31415 vs 31425 -> 4/5
res, err = engine.score_memory([3, 1, 4, 1, 5], "31415")
check("memory perfect 5/5", err is None and res["correct"] == 5
      and res["accuracy"] == 1.0, str(res))
res, err = engine.score_memory([3, 1, 4, 1, 5], "31425")
check("memory 4/5 = 0.8", err is None and res["correct"] == 4
      and res["accuracy"] == 0.8, str(res))
res, err = engine.score_memory([3, 1, 4, 1, 5], [3, 1, 4, 1, 5])
check("memory list answer ok", err is None and res["correct"] == 5)
_, err = engine.score_memory([3, 1, 4], "31")
check("memory wrong length rejected", err is not None)
_, err = engine.score_memory([3, 1, 4], "")
check("memory empty answer rejected", err is not None)

# --- Rang: Stroop ------------------------------------------------------------
r, err = engine.stroop_round(2, seed=11)
check("stroop 10 trials", err is None and len(r["trials"]) == 10
      and len(r["options"]) == 4, str(r))
check("stroop ink in options", all(t["ink"] in r["options"]
      for t in r["trials"]))
check("stroop congruent flag honest",
      all((t["word"] == t["ink"]) == t["congruent"] for t in r["trials"]))
r2, _ = engine.stroop_round(2, seed=11)
check("stroop seeded deterministic", r["trials"] == r2["trials"])

# hand-computed: 1 congruent right, 1 incongruent wrong -> 1/2
trials = [{"word": "laal", "ink": "laal", "congruent": True},
          {"word": "laal", "ink": "neela", "congruent": False}]
res, err = engine.score_stroop(trials, ["laal", "laal"])
check("stroop 1/2 hand", err is None and res["correct"] == 1
      and res["accuracy"] == 0.5 and res["congruent_correct"] == 1
      and res["congruent_total"] == 1 and res["incongruent_correct"] == 0
      and res["incongruent_total"] == 1, str(res))
_, err = engine.score_stroop(trials, ["laal"])
check("stroop short answers rejected", err is not None)

# --- Tez Hisab: maths ---------------------------------------------------------
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
       "x": lambda a, b: a * b, "/": lambda a, b: a // b}
bad = 0
for lvl in range(1, 6):
    for seed in range(50):
        q, err = engine.math_question(lvl, seed=seed)
        if err or q["answer"] != OPS[q["op"]](q["a"], q["b"]):
            bad += 1
        if lvl == 1 and q["op"] == "-" and q["answer"] < 0:
            bad += 1
        if lvl == 3 and q["op"] == "/" and q["a"] % q["b"] != 0:
            bad += 1
check("math 250 seeded answers exact", bad == 0, f"bad={bad}")
q, _ = engine.math_question(1, seed=3)
check("math L1 in range", 0 <= q["a"] <= 20 and 0 <= q["b"] <= 20)
q, _ = engine.math_question(3, seed=5)
check("math L3 mult/div small",
      (q["op"] == "x" and 2 <= q["a"] <= 12 and 2 <= q["b"] <= 12)
      or (q["op"] == "/" and q["a"] % q["b"] == 0))
q, _ = engine.math_question(5, seed=9)
check("math L5 two-digit",
      (q["op"] == "x" and 10 <= q["a"] <= 99 and 10 <= q["b"] <= 99)
      or (q["op"] == "-" and 100 <= q["a"] <= 999 and 10 <= q["b"] <= 99))
res, err = engine.check_math({"answer": 42}, 42)
check("math check right", err is None and res["correct"] is True)
res, err = engine.check_math({"answer": 42}, 41)
check("math check wrong", err is None and res["correct"] is False)
_, err = engine.check_math({"answer": 42}, "42")
check("math check non-int rejected", err is not None)

# --- Do Peeche: 2-back ---------------------------------------------------------
r, err = engine.nback_sequence(1, seed=21)
check("nback L1 14 letters", err is None and r["length"] == 14
      and len(r["letters"]) == 14 and len(r["targets"]) == 14, str(r))
check("nback first two never targets",
      r["targets"][0] is False and r["targets"][1] is False)
check("nback targets honest",
      all(r["targets"][i] == (r["letters"][i] == r["letters"][i - 2])
          for i in range(2, r["length"])))
check("nback target_count matches",
      r["target_count"] == sum(r["targets"]))
r, err = engine.nback_sequence(5, seed=21)
check("nback L5 22 letters", err is None and r["length"] == 22)
r2, _ = engine.nback_sequence(1, seed=21)
check("nback seeded deterministic", r2["letters"] == engine.nback_sequence(1, seed=21)[0]["letters"])

# hand-computed: targets F F T F T; answers F F T T F -> hits 1, miss 1, FA 1, CR 2, acc 0.6
res, err = engine.score_nback([False, False, True, False, True],
                              [False, False, True, True, False])
check("nback hand 0.6", err is None and res["hits"] == 1
      and res["misses"] == 1 and res["false_alarms"] == 1
      and res["correct_rejections"] == 2 and res["accuracy"] == 0.6,
      str(res))
_, err = engine.score_nback([True, False], [True])
check("nback length mismatch rejected", err is not None)

# --- Raasta: grid ---------------------------------------------------------------
r, err = engine.grid_round(1, seed=31)
check("grid L1 3x3 3 lit", err is None and r["size"] == 3
      and r["lit_count"] == 3 and len(r["lit"]) == 3
      and len(set(r["lit"])) == 3 and all(0 <= c <= 8 for c in r["lit"]),
      str(r))
r, err = engine.grid_round(5, seed=31)
check("grid L5 4x4 7 lit", err is None and r["size"] == 4
      and r["lit_count"] == 7 and len(r["lit"]) == 7
      and all(0 <= c <= 15 for c in r["lit"]))
r2, _ = engine.grid_round(1, seed=31)
r3, _ = engine.grid_round(1, seed=31)
check("grid seeded deterministic", r2["lit"] == r3["lit"])

# hand-computed: lit {1,5,8}, picked {1,5,7} -> tp 2, fp 1, fn 1, P=R=F1=0.667
res, err = engine.score_grid([1, 5, 8], [1, 5, 7], 3)
check("grid F1 0.667 hand", err is None and res["true_positives"] == 2
      and res["false_positives"] == 1 and res["false_negatives"] == 1
      and res["precision"] == 0.667 and res["recall"] == 0.667
      and res["f1"] == 0.667, str(res))
res, err = engine.score_grid([1, 5, 8], [1, 5, 8], 3)
check("grid perfect F1 1.0", err is None and res["f1"] == 1.0)
res, err = engine.score_grid([1, 5, 8], [], 3)
check("grid empty picked F1 0", err is None and res["f1"] == 0.0
      and res["precision"] == 0.0)
_, err = engine.score_grid([1, 5, 9], [1, 5, 99], 3)
check("grid out-of-range cell rejected", err is not None)

# --- Zehn Score -------------------------------------------------------------------
# hand: 70*acc + 30*speed; speed 1.0 at/under target, 0 at 2x target
s, err = engine.zehn_score(1.0, 8.0, 8.0)
check("score perfect 100", err is None and s["score"] == 100, str(s))
s, err = engine.zehn_score(1.0, 16.0, 8.0)
check("score perfect but 2x slow = 70", err is None and s["score"] == 70, str(s))
s, err = engine.zehn_score(0.5, 8.0, 8.0)
check("score half acc on time = 65", err is None and s["score"] == 65, str(s))
s, err = engine.zehn_score(0.5, 16.0, 8.0)
check("score half acc 2x slow = 35", err is None and s["score"] == 35, str(s))
s, err = engine.zehn_score(0.0, 100.0, 8.0)
check("score zero floor", err is None and s["score"] == 0)
s, err = engine.zehn_score(0.8, 12.0, 8.0)
check("score 0.8 acc 1.5x time = 71", err is None and s["score"] == 71, str(s))
_, err = engine.zehn_score(1.2, 8.0, 8.0)
check("score accuracy >1 rejected", err is not None)
_, err = engine.zehn_score(0.5, -1.0, 8.0)
check("score negative time rejected", err is not None)

# --- adaptive difficulty ------------------------------------------------------------
a, err = engine.adaptive_level(3, 0.9, 8.0, 8.0)
check("adapt up 3->4", err is None and a["new_level"] == 4
      and a["change"] == "up", str(a))
a, err = engine.adaptive_level(5, 0.95)
check("adapt max stays 5", err is None and a["new_level"] == 5
      and a["change"] == "max")
a, err = engine.adaptive_level(3, 0.4)
check("adapt down 3->2", err is None and a["new_level"] == 2
      and a["change"] == "down")
a, err = engine.adaptive_level(1, 0.2)
check("adapt min stays 1", err is None and a["new_level"] == 1
      and a["change"] == "min")
a, err = engine.adaptive_level(3, 0.65)
check("adapt stay 0.65", err is None and a["new_level"] == 3
      and a["change"] == "stay")
a, err = engine.adaptive_level(3, 0.9, 12.0, 8.0)
check("adapt accurate but slow stays", err is None
      and a["new_level"] == 3 and a["change"] == "stay", str(a))
_, err = engine.adaptive_level(0, 0.9)
check("adapt bad level rejected", err is not None)

# --- workout plan ---------------------------------------------------------------------
p, err = engine.workout_plan(100)
check("workout 5 distinct games", err is None and len(p["games"]) == 5
      and len({g["game"] for g in p["games"]}) == 5, str(p))
p2, _ = engine.workout_plan(101)
check("workout rotates by day",
      [g["game"] for g in p["games"]] != [g["game"] for g in p2["games"]])
p3, _ = engine.workout_plan(100)
check("workout deterministic same day",
      [g["game"] for g in p["games"]] == [g["game"] for g in p3["games"]])
p, err = engine.workout_plan(100, weakest="speed")
check("workout weakest first", err is None
      and p["games"][0]["skill"] == "speed", str(p))
_, err = engine.workout_plan(367)
check("workout day 367 rejected", err is not None)
_, err = engine.workout_plan(100, weakest="bogus")
check("workout bad skill rejected", err is not None)

# --- games catalogue ------------------------------------------------------------------
gl = engine.game_list()
check("game list 5 with targets", len(gl) == 5
      and all("target_seconds" in g for g in gl))
check("game list ids", {g["id"] for g in gl}
      == {"yaad", "rang", "hisab", "peeche", "raasta"})

# --- AI validators ----------------------------------------------------------------------
_, err = engine.validate_ai_tip("Too short.")
check("tip too short rejected", err is not None)
t, err = engine.validate_ai_tip(
    "Kal yaad ka khel khelein: digits ko teen-teen ke groups me "
    "yaad rakhein, aur aaram se khelein.")
check("tip good passes", err is None and t is not None)
_, err = engine.validate_ai_summary(
    "Sirf ek jumla hai yahan aur kuch nahi.")
check("summary 1 sentence rejected", err is not None)
s2, err = engine.validate_ai_summary(
    "Is hafte aapki memory sab se mazboot rahi. Speed par thora "
    "kaam karein, roz 5 minute hisab khelein.")
check("summary 2 sentences passes", err is None and s2 is not None)

# --- gemini no-key path ---------------------------------------------------------------------
check("gemini no key", gemini.key_available() is False)
_, err = gemini.daily_tip("roman", "memory 82, speed 54")
check("gemini tip no-key error", err is not None)
_, err = gemini.weekly_summary("en", "12 games, best memory 82")
check("gemini summary no-key error", err is not None)
_, err = gemini.daily_tip("xx", "memory 82")
check("gemini bad language rejected", err is not None)

# --- routes (TestClient) ------------------------------------------------------------------
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from zehn.routes import router  # noqa: E402

    app = FastAPI()
    app.include_router(router)
    c = TestClient(app)

    r = c.get("/zehn")
    check("route page 200", r.status_code == 200 and "Zehn" in r.text
          and "ذہن" in r.text)
    r = c.get("/zehn/api/games")
    check("route games 5", r.status_code == 200
          and len(r.json()["games"]) == 5)
    r = c.get("/zehn/api/ai-status")
    check("route ai-status no-key", r.status_code == 200
          and r.json()["ai_available"] is False)
    r = c.get("/zehn/api/memory?level=1&seed=7")
    check("route memory seeded", r.status_code == 200
          and r.json()["ok"] is True and len(r.json()["digits"]) == 3)
    r = c.post("/zehn/api/memory/score",
               data={"digits": "[3,1,4,1,5]", "answer": "31415"})
    check("route memory score 5/5", r.status_code == 200
          and r.json()["ok"] is True and r.json()["correct"] == 5)
    r = c.get("/zehn/api/stroop?level=2&seed=11")
    check("route stroop 10", r.status_code == 200
          and r.json()["ok"] is True and len(r.json()["trials"]) == 10)
    r = c.post("/zehn/api/stroop/score",
               data={"trials": '[{"ink": "laal", "congruent": true}]',
                     "answers": '["laal"]'})
    check("route stroop score 1/1", r.status_code == 200
          and r.json()["ok"] is True and r.json()["correct"] == 1)
    r = c.get("/zehn/api/math?level=3&seed=5")
    check("route math", r.status_code == 200 and r.json()["ok"] is True
          and "answer" in r.json())
    r = c.post("/zehn/api/math/check", data={"answer": 42, "given": 42})
    check("route math check", r.status_code == 200
          and r.json()["ok"] is True and r.json()["correct"] is True)
    r = c.get("/zehn/api/nback?level=1&seed=21")
    check("route nback 14", r.status_code == 200
          and r.json()["ok"] is True and len(r.json()["letters"]) == 14)
    r = c.post("/zehn/api/nback/score",
               data={"targets": "[false,false,true]",
                     "answers": "[false,false,true]"})
    check("route nback score", r.status_code == 200
          and r.json()["ok"] is True and r.json()["accuracy"] == 1.0)
    r = c.get("/zehn/api/grid?level=1&seed=31")
    check("route grid 3 lit", r.status_code == 200
          and r.json()["ok"] is True and len(r.json()["lit"]) == 3)
    r = c.post("/zehn/api/grid/score",
               data={"lit": "[1,5,8]", "picked": "[1,5,8]", "size": 3})
    check("route grid score F1 1.0", r.status_code == 200
          and r.json()["ok"] is True and r.json()["f1"] == 1.0)
    r = c.post("/zehn/api/score",
               data={"accuracy": 1.0, "avg_seconds": 8.0, "game": "yaad"})
    check("route score 100", r.status_code == 200
          and r.json()["ok"] is True and r.json()["score"] == 100)
    r = c.post("/zehn/api/score",
               data={"accuracy": 0.5, "avg_seconds": 8.0, "game": "bogus"})
    check("route score bad game", r.status_code == 200
          and r.json()["ok"] is False)
    r = c.post("/zehn/api/adapt",
               data={"level": 3, "accuracy": 0.9, "avg_seconds": 8.0,
                     "target_seconds": 8.0})
    check("route adapt up", r.status_code == 200
          and r.json()["ok"] is True and r.json()["new_level"] == 4)
    r = c.get("/zehn/api/workout?day=100&weakest=speed")
    check("route workout weakest first", r.status_code == 200
          and r.json()["ok"] is True
          and r.json()["games"][0]["skill"] == "speed")
    r = c.post("/zehn/api/tip-ai",
               data={"language": "roman", "score_summary": "memory 82"})
    check("route tip-ai no-key", r.status_code == 200
          and r.json()["ok"] is False)
    r = c.post("/zehn/api/summary-ai",
               data={"language": "en", "week_summary": "12 games"})
    check("route summary-ai no-key", r.status_code == 200
          and r.json()["ok"] is False)
except Exception as exc:  # noqa: BLE001 - surface as failures
    check("routes import/run", False, repr(exc))

print(f"PASS {PASS}  FAIL {len(FAIL)}")
for f in FAIL:
    print("FAIL:", f)
sys.exit(1 if FAIL else 0)

# RxLantern tokenomics

Model: **gpt-6-luna** through Portkey. Prices (US dollars per 1 million tokens): input **$0.10**, cached input **$0.01**, output **$0.50**; web search **$0.01 per search**. Source: https://api.portkey.ai/model-configs/pricing/openai/gpt-6-luna (Portkey lists cents per token; converted to dollars per 1M and confirmed with the project owner).

Data: the 11 Step 4 test questions run once in normal mode and once in "ask everyone" mode (`tests/cost_experiment.py`, raw results in `output/cost_experiment.json`). Cost per question = (input - cached input) x input price + cached input x cached price + output x output price.

## 1. Average tokens and cost per question (normal mode)

| | Input | Cached input | Output | Total (input + output) | Cost |
|---|---:|---:|---:|---:|---:|
| All 11 questions | 7,382 | 3,495 | 884 | 8,267 | $0.000866 |
| 9 questions the model answered | 9,023 | 4,271 | 1,081 | 10,104 | $0.001058 |

Cached input tokens are part of the input count (OpenAI counts them inside input). Output tokens cost 5x input, so output is 51% of the cost while being 11% of the tokens.

## 2. What prompt caching saved

- Input tokens: 81,205. Of these, 38,440 (47%) were read from OpenAI's prompt cache.
- Cached tokens cost $0.01 per 1M instead of $0.10: a 90% discount.
- Saved: 38,440 x ($0.10 - $0.01) / 1,000,000 = **$0.003460** on these 11 questions.
- Cost with caching $0.009526 vs. $0.012986 without: **27% cheaper**.
- Why it works: each prompt file puts the long fixed instructions first and today's date/time last, and each agent sends a stable `prompt_cache_key`, so repeat calls reuse the same prefix. Caching only starts once a prefix is long enough and has been seen recently, so the first question of the day caches less.

## 3. What the code-level rules saved

- 2 of 11 questions (18%) were answered by code with **0 tokens**: Q6 (medical advice declined); Q10 (follow-up asked (unclear question)).
- If the model had handled them like a normal question: 2 x 10,104 tokens = **20,207 tokens** and 2 x $0.001058 = **$0.002117** saved.
- These rules are also safer: the model never sees a medical-advice question, and never guesses a hospital.
- Other code rules that cost nothing: the daily token budget and the per-visitor rate limit refuse before any model call (see `output/limit_tests.json`).

## 4. Cost per user per month

Assumption: **4 questions per patient per month**, with the same mix as the 11 test questions (average $0.000866 per question, normal mode).

| Users | Math | Monthly cost (normal mode) | Monthly cost if every question asked all three specialists |
|---:|---|---:|---:|
| 1 | 1 x 4 x $0.000866 | **$0.0035** | $0.0069 |
| 100 | 100 x 4 x $0.000866 | **$0.35** | $0.69 |
| 10,000 | 10,000 x 4 x $0.000866 | **$34.64** | $68.92 |

- One patient: 4 x $0.000866 = $0.003464 per month.
- 100 users: 100 x $0.003464 = $0.3464 per month (400 questions).
- 10,000 users: 10,000 x $0.003464 = $34.64 per month (40,000 questions, about 11,022,061 tokens a day).
- Daily budget check: the app's daily budget is 3,000,000 tokens, enough for about 363 questions a day at today's average. 10,000 users would need the budget raised.
- Not included: web searches for holiday hours cost $0.01 each, about 9x a normal answer, which is why holiday results are cached for 24 hours and saved holiday hours are used first. Hosting, Portkey fees, and staff time are also not included.

## 5. Did cost-cutting hurt quality? (cost experiment)

Same 11 questions, two modes. "Passed" = the answer followed the rules and gave the key fact for that question (automatic checks in `tests/cost_experiment.py`, spot-checked by hand). The code safety rules stay on in both modes, so Q6 and Q10 use 0 tokens in both.

| # | Question | Normal: specialists | Normal: tokens | Normal: cost | Ask everyone: specialists | Ask everyone: tokens | Ask everyone: cost | Passed (normal / everyone) |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Is there a pharmacy open right now near 02111? | 1 | 10,597 | $0.001284 | 3 | 17,680 | $0.002465 | yes / yes |
| 2 | Is Concerta 18 mg in shortage? Which pharmacy has it? | 1 | 9,043 | $0.000726 | 3 | 14,599 | $0.001437 | yes / yes |
| 3 | How much will Eliquis 5 mg cost me with Medicare? | 1 | 8,245 | $0.000842 | 3 | 15,884 | $0.001911 | yes / yes |
| 4 | Does MassHealth cover Ozempic? | 1 | 8,683 | $0.000543 | 3 | 14,116 | $0.001417 | yes / yes |
| 5 | Where can I get a flu shot in Chinatown, and does Blue Cr... | 2 | 18,043 | $0.002399 | 3 | 29,789 | $0.004139 | yes / yes |
| 6 | My sumatriptan didn't work. Should I take two? | 0 | 0 | $0.000000 | 0 | 0 | $0.000000 | yes / yes |
| 7 | ¿Qué farmacia en East Boston tiene entrega a domicilio? | 1 | 6,598 | $0.000715 | 3 | 13,123 | $0.001739 | yes / yes |
| 8 | Will my kid's amoxicillin liquid be covered? We have Blue... | 1 | 9,930 | $0.001004 | 3 | 15,481 | $0.001828 | yes / yes |
| 9 | Is the CVS at South Station open on weekends? | 1 | 9,726 | $0.000914 | 3 | 15,570 | $0.001557 | yes / yes |
| 10 | How close is an urgent care or clinic to the hospital? | 0 | 0 | $0.000000 | 0 | 0 | $0.000000 | yes / yes |
| 11 | Is there a walk-in clinic near the CVS in Mattapan? | 1 | 10,067 | $0.001099 | 3 | 22,787 | $0.002458 | yes / yes |
| | **Total** | 10 | **90,932** | **$0.009526** | 27 | **159,029** | **$0.018951** | 11/11 / 11/11 |

**Result:** normal mode used **43% fewer tokens** and cost **50% less** than asking all three specialists, with the same quality (11/11 vs 11/11 passed). Calling the extra specialists added tokens without making any answer pass that failed before.

Limits of this evidence: 11 questions, one run per mode, and automatic checks look for key facts and rules, not writing quality. Model answers vary a little from run to run.

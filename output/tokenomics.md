# RxLantern tokenomics

Model: **gpt-6-luna** through Portkey. Prices (US dollars per 1 million tokens): input **$0.10**, cached input **$0.01**, output **$0.50**; web search **$0.01 per search**. Source: https://api.portkey.ai/model-configs/pricing/openai/gpt-6-luna (Portkey lists cents per token; converted to dollars per 1M and confirmed with the project owner).

Data: the 11 Step 4 test questions run once in normal mode and once in "ask everyone" mode on 2026-10-24 23:46 (Boston time) (`tests/cost_experiment.py`, raw results in `output/cost_experiment.json`). Cost per question = (input - cached input) x input price + cached input x cached price + output x output price. These are the numbers in the final report.

## 1. Average tokens and cost per question (normal mode)

| | Input | Cached input | Output | Total (input + output) | Cost |
|---|---:|---:|---:|---:|---:|
| All 11 questions | 9,436 | 4,793 | 1,149 | 10,585 | $0.001087 |
| 9 questions the model answered | 11,533 | 5,858 | 1,404 | 12,937 | $0.001328 |

Cached input tokens are part of the input count (OpenAI counts them inside input).

## 2. What prompt caching saved

- Input tokens: 103,797. Of these, 52,724 (51%) were read from the prompt cache.
- Cached tokens cost $0.01 per 1M instead of $0.10: a 90% discount.
- Saved: 52,724 x ($0.10 - $0.01) / 1,000,000 = **$0.004745** on these 11 questions.
- Cost with caching $0.011954 vs. $0.016699 without: **28% cheaper**.

## 3. What the code-level rules saved

- 2 of 11 questions were answered by code with **0 tokens**: Q6 (medical advice declined); Q10 (follow-up asked (unclear question)).
- If the model had handled them like a normal question: 2 x 12,937 tokens = **25,874 tokens** and 2 x $0.001328 = **$0.002656** saved.

## 4. Cost per user per month

Assumption: **4 questions per patient per month**, with the same mix as the 11 test questions (average $0.001087 per question, normal mode).

| Users | Math | Monthly cost (normal mode) | Monthly cost if every question asked all three specialists |
|---:|---|---:|---:|
| 1 | 1 x 4 x $0.001087 | **$0.0043** | $0.0075 |
| 100 | 100 x 4 x $0.001087 | **$0.4348** | $0.7540 |
| 10,000 | 10,000 x 4 x $0.001087 | **$43.4800** | $75.4000 |

- Daily budget check: the app's daily budget is 3,000,000 tokens, enough for about 283 questions a day at this average. 10,000 users (about 14,113,333 tokens a day) would need the budget raised.
- Not included: web searches for holiday hours ($0.01 each, cached 24 hours), hosting, Portkey fees, and staff time.

## 5. Did cost-cutting hurt quality? (cost experiment)

Same 11 questions, two modes. "Passed" = the answer followed the rules and gave the key fact for that question (automatic checks in `tests/cost_experiment.py`). The code safety rules stay on in both modes.

| # | Question | Normal: specialists | Normal: tokens | Normal: cost | Ask everyone: specialists | Ask everyone: tokens | Ask everyone: cost | Passed (normal / everyone) |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Is there a pharmacy open right now near 02111? | 1 | 16,186 | $0.001754 | 3 | 23,609 | $0.002860 | yes / yes |
| 2 | Is Concerta 18 mg in shortage? Which pharmacy has it? | 1 | 9,590 | $0.000590 | 3 | 16,272 | $0.001408 | yes / yes |
| 3 | How much will Eliquis 5 mg cost me with Medicare? | 1 | 10,458 | $0.000848 | 3 | 17,480 | $0.001789 | yes / yes |
| 4 | Does MassHealth cover Ozempic? | 1 | 9,367 | $0.000789 | 3 | 16,127 | $0.001769 | yes / yes |
| 5 | Where can I get a flu shot in Chinatown, and does Blue Cr... | 2 | 29,890 | $0.003772 | 3 | 41,234 | $0.003899 | yes / yes |
| 6 | My sumatriptan didn't work. Should I take two? | 0 | 0 | $0.000000 | 0 | 0 | $0.000000 | yes / yes |
| 7 | ¿Qué farmacia en East Boston tiene entrega a domicilio? | 1 | 7,300 | $0.000677 | 3 | 20,476 | $0.002439 | yes / yes |
| 8 | Will my kid's amoxicillin liquid be covered? We have Blue... | 1 | 12,199 | $0.001536 | 3 | 19,336 | $0.002751 | yes / yes |
| 9 | Is the CVS at South Station open on weekends? | 1 | 10,476 | $0.000949 | 3 | 21,176 | $0.001736 | yes / yes |
| 10 | How close is an urgent care or clinic to the hospital? | 0 | 0 | $0.000000 | 0 | 0 | $0.000000 | yes / yes |
| 11 | Is there a walk-in clinic near the CVS in Mattapan? | 1 | 10,969 | $0.001039 | 3 | 21,327 | $0.002087 | yes / yes |
| | **Total** | 10 | **116,435** | **$0.011954** | 27 | **197,037** | **$0.020738** | 11/11 / 11/11 |

**Result:** normal mode used **41% fewer tokens** and cost **42% less** than asking all three specialists, with 11/11 vs. 11/11 answers passing.

Limits of this evidence: 11 questions, one run per mode, and automatic checks look for key facts and rules, not writing quality. Model answers vary from run to run. The 4 questions a month is an assumption.

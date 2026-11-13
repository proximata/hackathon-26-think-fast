# Further resources (optional)

Extra material for teams who want to go deeper. Nothing here is required, and none of it changes how you're judged ([CASE.md](../CASE.md)).

## Applied Deep Learning (CEU)

[Applied Deep Learning](https://earino.github.io/applied-deep-learning/) is a six-week course by E. Ariño de la Rubia (CC BY 4.0). Its notebooks run on free Kaggle or Colab GPUs. It works on a classifier rather than a decision engine, but most of its techniques carry straight over to the decision API, where your engine returns a probability per answer:

| Your step | What to take from the course |
|---|---|
| Make it honest | [Pre-work](https://earino.github.io/applied-deep-learning/site/pre-work.html) on calibration, and [week 4](https://earino.github.io/applied-deep-learning/site/week4.html): calibration error, temperature scaling, and choosing a confidence threshold from data |
| Make it yours | Pre-work on LoRA and distillation, and [week 6](https://earino.github.io/applied-deep-learning/site/week6.html): training a small student on a bigger teacher's saved probabilities. For a decision engine, the teacher can be a larger local model answering the same questions through the API |
| Make it fast and cheap | [Week 5](https://earino.github.io/applied-deep-learning/site/week5.html): measuring latency, memory and cost before and after quantization, and comparing against a bigger model |
| Prove it | The course's memos: bootstrap ranges on every comparison, results on the weakest slice, and a defended "what would you ship" call |

Three of its measured lessons that apply to decision engines:

- **Try temperature scaling before distillation.** One fitted number beat an 80-minute distillation run on calibration error ([blog](https://earino.github.io/applied-deep-learning/site/blog/12_temperature_scaling_beats_distillation.html)). For a decision engine, that means rescaling the probabilities it returns.
- **Measure before you quantize.** bitsandbytes int8 ran about 2.5× slower than fp16 on sub-7B models on a T4 GPU, and used more memory ([blog](https://earino.github.io/applied-deep-learning/site/blog/11_int8_is_slower.html)). On a CPU, GGUF with llama.cpp is the usual route.
- **Data beats scale on a long tail.** With the same fine-tuning setup, 1.5B, 3B and 8B models scored 0.250, 0.270 and 0.271 macro F1 ([blog](https://earino.github.io/applied-deep-learning/site/blog/08_cant_scale_out_of_data_problem.html)). Better training data usually beats a bigger model.

## Showing your evidence

Optional rows in [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) follow the same habits:

- Resample your test set (a bootstrap) to show the range of the gain over your baseline.
- Report how the engine does on its weakest slice, such as the rarest answers.
- Say what you'd ship, and when the big hosted model would still be worth its price.

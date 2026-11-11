# Evaluation

## RAG (book assistant)

Notebook: [RAGEval.ipynb](RAGEval.ipynb)
Results: [results/rag_qa_call_of_the_wild.csv](results/rag_qa_call_of_the_wild.csv)

30 questions from the NarrativeQA test set on The Call of the Wild. Retrieval weights: 0.6 vector, 0.4 BM25.

| Metric | Mean |
|---|---|
| Token F1 | 0.115 |
| Human score (0 to 1) | 0.711 |

17/30 answers were fully correct. F1 is low mostly because the reference answers are one or two words and the assistant answers in full sentences.

## Summarization

Notebook: [eval_summary.ipynb](eval_summary.ipynb)
Results: [results/chapter_summaries_scored.csv](results/chapter_summaries_scored.csv)

Generated chapter summaries compared with SparkNotes chapter summaries.

| Book | Chapters | ROUGE-L | BERTScore F1 |
|---|---|---|---|
| Alice in Wonderland | 12 | 0.152 | 0.842 |
| Dracula | 27 | 0.166 | 0.851 |
| All | 39 | 0.162 | 0.848 |

The SparkNotes summaries are not included since they are copyrighted. The input CSVs used by the notebooks are also not included.

To run RAGEval.ipynb, set OPENAI_API_KEY as an environment variable .

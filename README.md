# Will the Model Look for the Answer?

A simple experiment with **Gemma 4 12B** testing whether an LLM will voluntarily use an available file-reading tool when told that the file contains the answer to a difficult problem.

## Experiment

The model receives:

* A challenging math problem
* Knowledge that `answer.txt` contains the answer
* Access to a `read_file` tool
* Freedom to decide whether to use the tool

The model is **not instructed to read the file**.

The key question:

> **When given access to the answer, will the model choose to look for it?**

## Setup

```text
.
├── experiment.py
├── scenario.py
├── prompt.py
├── answer.txt
└── outputs/
    ├── run_01/
    │   └── result.txt
    └── ...
```

## Model

```text
gemma4:12b
```

Run locally with [Ollama](https://ollama.com/).

## Running

Change the number of runs:

```python
NUM_RUNS = 5
```

Then:

```bash
python experiment.py
```

Each run is saved separately and existing runs are never overwritten.

## Recorded

Each run captures:

* Model thinking
* Initial response
* Tool calls
* File accessed
* File contents returned
* Final thinking
* Final answer

## Core Observation

The experiment does not force tool use.

It observes whether the model **chooses to seek information that it knows is available**.

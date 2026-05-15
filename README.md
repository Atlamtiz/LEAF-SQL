<div align="center">

# 🍃 LEAF-SQL

### Level-wise Exploration with Adaptive Fine-graining for Text-to-SQL Skeleton Prediction

[![Paper](https://img.shields.io/badge/arXiv-2605.09295-b31b1b.svg)](https://arxiv.org/abs/2605.09295)
[![Conference](https://img.shields.io/badge/ICDE-2026-blue.svg)](https://arxiv.org/abs/2605.09295)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)

**Official implementation of the LEAF-SQL paper.**

[📄 Paper](https://arxiv.org/abs/2605.09295) · [💻 Code](https://github.com/Atlamtiz/LEAF-SQL) · [✉️ Contact](mailto:tanzhao325@gmail.com)

</div>

---

## 🎉 News

- **\[2026\]** 🏆 LEAF-SQL has been **accepted to ICDE 2026**! Read the paper on [arXiv](https://arxiv.org/abs/2605.09295).

---

## 📖 Introduction

**LEAF-SQL** is a framework that treats Text-to-SQL as a **tree search problem**, exploring multiple skeleton candidates with diverse structures and granularities to improve the final query's accuracy.

<div align="center">
  <img src="./img/method_level_wise_skeleton_search.png" width="80%" alt="LEAF-SQL method overview">
</div>

---

## 🚀 Quick Start

For a quick demonstration of the LEAF-SQL method, you can run the example script. Note that this is a simplified version and does not represent the full functionality.

```bash
python example.py
```

---

## 🏁 Standard Usage

Follow these steps for the complete setup and execution.

### Step 1 · Install Dependencies

Install all the required packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Step 2 · Download Models and Dataset

Download the necessary models from ModelScope:

```bash
# Download the SkeEva model
modelscope download --model mrtanzhao/SkeEva --local_dir ./models/skeeva

# Download the SkeFor model
modelscope download --model Qwen/Qwen3-14B --local_dir ./models/skefor
```

Download the BIRD dataset from the official website: <https://bird-bench.github.io/>

### Step 3 · Configure Settings

Modify the configuration file `./config/config.yaml` to match your environment settings (e.g., file paths, `api_key`).

### Step 4 · Launch API Servers

Start the two model services in separate terminal sessions. Adjust the parameters (like `CUDA_VISIBLE_DEVICES`, `tensor-parallel-size`, etc.) according to your hardware specifications.

> The following example assumes an **8-GPU environment**, assigning 4 GPUs to each model for optimal performance.

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 python -m vllm.entrypoints.openai.api_server \
    --model ./models/skefor \
    --served-model-name skefor \
    --port 8001 \
    --tensor-parallel-size 4 \
    --max-num-seqs 32 \
    --max-num-batched-tokens 1024
```

```bash
CUDA_VISIBLE_DEVICES=4,5,6,7 python -m vllm.entrypoints.openai.api_server \
    --model ./models/skeeva \
    --served-model-name skeeva \
    --port 8002 \
    --tensor-parallel-size 4 \
    --max-num-seqs 32 \
    --max-num-batched-tokens 1024
```

### Step 5 · Run the Main Program

Once the services are running, execute the main script. You will see a progress bar indicating the processing status of the tasks.

```bash
python main.py
```

---

## 🌈 Contact Us

This project welcomes contributions and suggestions 👍.

If you find a bug, encounter a problem, or have a suggestion for LEAF-SQL, please [submit an issue](https://github.com/Atlamtiz/LEAF-SQL/issues) or reach out via email at **tanzhao325@gmail.com**.

---

## 📝 Citation

If you find our work useful or inspiring, please consider citing:

```bibtex
@inproceedings{leaf-sql-icde2026,
  author    = {Zhao Tan and
               Xiping Liu and
               Qing Shu and
               Qizhi Wan and
               Dexi Liu and
               Changxuan Wan},
  title     = {LEAF-SQL: Level-wise Exploration with Adaptive Fine-graining for Text-to-SQL Skeleton Prediction},
  booktitle = {Proceedings of the 42nd IEEE International Conference on Data Engineering (ICDE)},
  year      = {2026}
}
```

You may also cite the preprint:

```bibtex
@article{leaf-sql-arxiv,
  author  = {Zhao Tan and
             Xiping Liu and
             Qing Shu and
             Qizhi Wan and
             Dexi Liu and
             Changxuan Wan},
  title   = {LEAF-SQL: Level-wise Exploration with Adaptive Fine-graining for Text-to-SQL Skeleton Prediction},
  journal = {arXiv preprint arXiv:2605.09295},
  year    = {2026}
}
```

---

## 📜 License

This project is released under the [MIT License](LICENSE).

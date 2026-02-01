---
layout: post
title: Transformers — What they are and main architectures
date: 2026-01-31
excerpt: "A short overview of what a Transformer is and the main types of transformer architectures (encoder-only, decoder-only, encoder-decoder, vision, vision-language), with examples and typical use."
categories:
  - "Deep Learning & AI"
tags:
  - Transformers
  - BERT
  - GPT
  - Vision-Language
  - Grounding DINO
---

In neural-network architecture, when people talk about "types of transformers" they usually mean the following.

---

## 1. What is a Transformer?

A **Transformer** is a neural-network architecture based on **attention**: instead of processing the sequence or the image in one go, each "position" (token or region) can **attend** to other positions and combine their information. In this way long-range relations are captured (e.g. one object on the left and another on the right). The core building blocks are **self-attention** and **feed-forward** layers; there are no classical convolutions in the core (although some vision models use convolutional or window-based components in the backbone).

### Attention formula (Q, K, V)

The core operation is **scaled dot-product attention**. Given query matrix {% raw %}$Q${% endraw %}, key matrix {% raw %}$K${% endraw %}, and value matrix {% raw %}$V${% endraw %} (with key dimension {% raw %}$d_k${% endraw %}), the output is:

{% raw %}
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right) V$$
{% endraw %}

So: affinity scores are {% raw %}$QK^T / \sqrt{d_k}${% endraw %}, softmax gives weights that sum to 1, and the output is the weighted combination of {% raw %}$V${% endraw %}.

---

## 2. Main types of transformer architectures

| Type | Example | Typical use |
|------|---------|-------------|
| **Encoder only** | BERT, ViT (vision only) | Classification, NER, embeddings. |
| **Decoder only** | GPT, LLaMA | Text generation. |
| **Encoder–decoder** | T5, BART | Translation, summarisation, encoder–decoder tasks. |
| **Vision Transformer (ViT)** | ViT, Swin | Image classification / detection. |
| **Vision–language** | CLIP, Grounding DINO | Image + text (e.g. text-guided detection). |

---

## 3. Vision–language and Grounding DINO

**Grounding DINO** belongs to the **vision–language** type: it takes an image and text prompts and returns bounding boxes (and labels) for the concepts described by the text. Internally it uses components in the spirit of **DETR** (encoder–decoder over the image) plus **fusion with text** (cross-attention between image and text, language-guided query selection, etc.).

I use the **vision–language** architecture in practice for text-guided object detection. For how Grounding DINO is used in this project (API, code, deployment), see [Grounding DINO — Model Overview and Concepts]({% post_url 2026-01-31-grounding-dino-overview %}).

---

To visualize the Q, K, V mechanism and the attention formula above, I recommend [Visualised Attention in Transformers](https://www.youtube.com/watch?v=RNF0FvRjGZk) and [3Blue1Brown — Attention in transformers, visually](https://www.youtube.com/watch?v=eMlx5fFNoYc).

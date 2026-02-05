# Zero-Shot Object Detection Service

**Habits** · Subproject: *PyTorch, TorchVision, Transformers, Grounding DINO, FastAPI*

---

## What is it for?

It lets **Habits** app users upload a **photo of their meal** (plate, tray) and automatically get:

- A **list of detected ingredients/foods** in the image (with labels in English, translated to Spanish on the frontend)
- Optionally an **image with segmentation** (where each detected ingredient is located)

The model **is not trained specifically** on those meals: it uses **zero-shot** text-guided detection (vision–language). So the user can "log food" with a photo and have the app suggest ingredients to confirm or edit before saving.

---

## How does it work?

1. In the **Nutrition** section of Habits, the user chooses "Log meal" and optionally "Attach photo" for a meal (breakfast, lunch, snack, dinner).
2. The frontend sends the image to the **Nutri-AI Backend** (Zero-Shot Object Detection Service) at the `/detect` endpoint (ingredient list only) and/or `/detect/image` (segmented image as JPEG).
3. The backend loads **Grounding DINO** (Hugging Face **Transformers** model): a text-guided object detection model that can detect objects described in natural language without class-specific training.
4. A list of **ingredient categories** is defined in text (e.g. rice, egg, chicken, lettuce, bread); the model receives the image and those texts and returns **bounding boxes** with label and score for each detection.
5. Thresholds (score, NMS) are applied and the list of detected ingredients is returned (and, if requested, the image with boxes drawn). The frontend translates labels to Spanish with a fixed mapping and shows them so the user can confirm or remove before saving the meal.

The whole pipeline is **zero-shot**: no need to train the model on "my dishes"; it's enough to describe in text what you want to detect.

---

## Implementation

- **API:** **FastAPI** with endpoints `/detect` (JSON with list of ingredients: label, score, box) and `/detect/image` (response with segmented JPEG image). The image is sent via `multipart` or as body; **Pillow** is used to open it and pass it to the model.
- **Model:** **Grounding DINO** via the **Transformers** library (Hugging Face): `AutoModelForZeroShotObjectDetection` and `AutoProcessor`. The model is loaded on demand (lazy) on the first request and runs with **PyTorch** on CPU or GPU depending on availability.
- **Stack:** **PyTorch** and **TorchVision** for tensors and image operations; **Transformers** for the model and processor; **Pillow** for image I/O; **FastAPI** + **Uvicorn** for the server; **python-multipart** for file uploads.
- **Configuration:** Parameters such as `BOX_THRESHOLD`, `TEXT_THRESHOLD`, and the model ID on Hugging Face are centralized in `detection/config.py`; the ingredient/category list is built from a string or list of texts.
- **Deployment:** Standalone Python service (Docker); the model is downloaded from Hugging Face the first time it's used. The frontend uses `VITE_NUTRI_AI_API_URL` to call this microservice.

In summary: **PyTorch** and **TorchVision** as the computation backend, **Transformers** and **Grounding DINO** for zero-shot detection, and **FastAPI** to expose the service within **Habits**.

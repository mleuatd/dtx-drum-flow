# Reference-model provider adapters

The deterministic downstream pipeline must not depend on one AI provider.

Provider adapters may populate the canonical multiview landmark schema from pose, segmentation, vision-AI or manual review. Every point must include/retain provider and confidence metadata. Downstream tools consume only the canonical JSON schema.

Current built-in mode: manual/template + OpenCV silhouette. External AI/pose providers are optional and must never become rendering authority.
